from __future__ import absolute_import
from flask import request, abort, current_app, json
import six
from sqlalchemy.orm.exc import NoResultFound
import requests
from base64 import urlsafe_b64encode, b64encode

from .oauth import OAuthMethod, OAuthUser
from .. import db
from .models import Group, Pilot


class BraveNeuCore(OAuthMethod):

    def __init__(self, devtest=False, **kwargs):
        """:py:class:`~.AuthMethod` using EVE SSO for authentication and BRAVE 
            Collective's NeuCore service for authorization.

        :param list admins: Two types of values are accepted as values in this
            list, either a string specifying a user's primary character's name,
            or their EVE Character ID as an integer.
        :param bool devtest: Testing parameter that changes the default domain
            for URLs from 'https://account.bravecollective.com' to
            'https://brvneucore.herokuapp.com`. Default: ``False``.
        :param str authorize_url: The URL to request OAuth authorization
            tokens. Default:
            ``'https://login.eveonline.com/oauth/authorize'``.
        :param str access_token_url: The URL for OAuth token exchange. Default:
            ``'https://login.eveonline.com/oauth/token'``.
        :param str base_url: The base URL for API requests. Default:
            ``'https://account.bravecollective.com/api/app/v1'``.
        :param dict request_token_params: Additional parameters to include with
            the authorization token request. Default: ``{'scope':
            ''}``.
        :param str access_token_method: HTTP Method to use for exchanging
            authorization tokens for access tokens. Default: ``'POST'``.
        :param int core_id: BRAVE NeuCore application ID.
        :param str core_secret: BRAVE NeuCore application secret.
        :param str name: The name for this authentication method. Default:
            ``'BRAVE NeuCore'``.
        """
        self.sso = 'https://login.eveonline.com'
        self.core = 'https://account.bravecollective.com'
        core_id = kwargs.get('core_id')
        core_secret = kwargs.get('core_secret')
        core_bearer = 'Bearer ' + b64encode(str(core_id) + ':' + core_secret)
        self.core_session = requests.Session()
        self.core_session.headers.update({'Authorization': core_bearer})
        if devtest:
            self.core = 'https://brvneucore.herokuapp.com'
        self.base_url = self.core + '/api/app'
        self.verify_url = self.sso + '/oauth/verify/'
        kwargs.setdefault('authorize_url',
                self.sso + '/oauth/authorize')
        kwargs.setdefault('access_token_url',
                self.sso + '/oauth/token')
        kwargs.setdefault('refresh_token_url',
                self.sso + '/oauth/token')
        kwargs.setdefault('scope', '')
        kwargs.setdefault('method', 'POST')
        kwargs.setdefault('app_key', 'BRAVE_NEUCORE')
        kwargs.setdefault('name', u'BRAVE NeuCore')
        kwargs.setdefault('secret_in_body', False)
        super(BraveNeuCore, self).__init__(**kwargs)

    def _get_user_data(self):
        if not hasattr(request, '_auth_user_data'):
            resp = self.session.get(self.verify_url)
            try:
                current_app.logger.debug(u"SSO Verify Response: {}".format(
                        resp.text))
                cid = resp.json().get('CharacterID')
            except TypeError:
                abort(500, u"Error in receiving Verify response {}".format(
                        resp))
            try:
                resp = self.core_session.get(self.base_url + '/v1/main/{}'.format(cid))
                current_app.logger.debug(u"BRAVE Core API response: {}".format(
                        resp.text))
                request._auth_user_data = resp.json()
                resp = self.core_session.get(self.base_url + '/v1/groups/{}'.format(cid))
                current_app.logger.debug(u"BRAVE Core API response: {}".format(
                        resp.text))
                request._auth_user_data[u'groups'] = resp.json()
                resp = self.core_session.get(self.base_url + '/v1/characters/{}'.format(cid))
                current_app.logger.debug(u'BRAVE Core API response: {}'.format(
                        resp.text))
                request._auth_user_data[u'characters'] = resp.json()
            except TypeError:
                abort(500, u"Error in receiving BRAVE API response: {}".format(
                        resp))
        current_app.logger.debug('Core User Data: {}'.format(request._auth_user_data))
        return request._auth_user_data

    def get_user(self):
        data = self._get_user_data()
        primary_character = data[u'name']
        user_id = data[u'id']
        try:
            user = BraveOauthUser.query.filter_by(auth_id=user_id,
                    authmethod=self.name).one()
            # The primary character can change
            user.name = primary_character
        except NoResultFound:
            user = BraveOauthUser(primary_character, user_id, self.name)
            db.session.add(user)
            db.session.commit()
        return user

    def is_admin(self, user):
        data = self._get_user_data()
        return super(BraveNeuCore, self).is_admin(user) or \
                user.auth_id in self.admins or \
                u'srp.admin' in [g[u'name'] for g in data[u'groups']]

    def get_pilots(self):
        pilots = []
        data = self._get_user_data()
        current_app.logger.debug(u'Adding pilots')
        for character in data[u'characters']:
            pilot = Pilot.query.get(int(character[u'id']))
            if pilot is None:
                pilot = Pilot(None, character[u'name'], character[u'id'])
            pilots.append(pilot)
            current_app.logger.debug(u'Added alt pilot {}'.format(pilot))
        current_app.logger.debug(u'Added pilots: {}'.format(pilots))
        return pilots

    def get_groups(self):
        data = self._get_user_data()
        groups = []
        try:
            for group_info in data[u'groups']:
                group_name = group_info[u'name']
                group_id = group_info[u'id']
                try:
                    group = BraveOauthGroup.query.filter_by(auth_id=group_id,
                            authmethod=self.name).one()
                except NoResultFound:
                    group = BraveOauthGroup(group_name, group_id, self.name)
                    db.session.add(group)
                if group.name != group_name:
                    group.name = group_name
                groups.append(group)
            db.session.commit()
        except KeyError as e:
            current_app.logger.debug("Couldn't add groups, missing key: {}".format(e))
        return groups


class BraveOauthUser(OAuthUser):

    id = db.Column(db.Integer, db.ForeignKey(OAuthUser.id), primary_key=True)

    auth_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    def __init__(self, username, auth_id, authmethod, groups=None, **kwargs):
        self.auth_id = auth_id
        super(BraveOauthUser, self).__init__(username, authmethod, **kwargs)


class BraveOauthGroup(Group):

    id = db.Column(db.Integer, db.ForeignKey(Group.id), primary_key=True)

    auth_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    def __init__(self, name, auth_id, authmethod, **kwargs):
        self.auth_id = auth_id
        super(BraveOauthGroup, self).__init__(name, authmethod, **kwargs)
