import os

# Should be set to a random string, like the output of os.urandom(24). Needs to
# be a static value that won't change between running the application.
SECRET_KEY = os.environ['SECRET_KEY']

# Set to the domain name for the app. It fixes things with static files and
# creating external links.
SERVER_NAME = os.environ['DOMAIN_NAME']
PREFERRED_URL_SCHEME = u'https'

SQLALCHEMY_DATABASE_URI = (os.environ['DATABASE_CONNECTION_STRING'])

# Used as the HTTP user agent for external API requests (like for CREST and
# zKillboard).
SRP_USER_AGENT_EMAIL = u'yukiko.kami.san@gmail.com'

SRP_AUTH_METHODS = [
    {
        # The 'type' key is an importable path followed by the name of the
        # AuthMethod class, separated either by a dot or a colon.
        'type': 'evesrp.auth.braveneucore.BraveNeuCore',
        # You can specify users to treat a site-wide administrators via the
        # 'admins' key. The value to this key is a list of strings (in the
        # special case of some AuthMethods, integers are also acceptable values
        # for the list.). This is very useful when first setting up the app, as
        # only site-wide administrators can create divisions.
        'admins': [u'Yukiko Kami', u'Rangvaldr'],
        # The OAuth consumer key and secret.
        # You can set a different name for an auth method here. This name is
        # shown to users, and should not be changed (and cannot without a lot
        # of manual mucking about in the database).
        'name': u'EVESSONeucore',
        'core_id': os.environ['CORE_APP_ID'],
        'core_secret': os.environ['CORE_APP_SECRET'],
        'client_id': os.environ['EVE_CLIENT_ID'],
        'client_secret': os.environ['EVE_CLIENT_SECRET']
    }
]

# You can specify custom killmail handling classes here. The instance folder is
# added to the import search path, so the modules can be placed in there.
SRP_KILLMAIL_SOURCES = [
    'evesrp.killmail.ZKillmail',
]

SRP_SHIP_TYPE_URL_TRANSFORMERS = [
    (u'BRAVE Wiki Fits',
        'https://wiki.bravecollective.com/member/alliance/military/doctrines/ships/{}'),
]

SRP_PILOT_URL_TRANSFORMERS = [
]

# You can set a custom name for your site here
SRP_SITE_NAME = 'Brave Collective SRP'
