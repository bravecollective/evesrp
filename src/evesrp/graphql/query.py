import functools

import graphene

from evesrp.graphql import types, pagination
from evesrp import graphql
from evesrp import new_models as models
from evesrp import storage


class Query(graphene.ObjectType):

    identity = graphene.Field(types.IdentityUnion,
                              uuid=graphene.Argument(
                                  graphene.ID,
                                  required=True
                              ),
                              key=graphene.Argument(
                                  graphene.ID,
                                  required=True
                              ))

    user = graphene.Field(types.User,
                          id=graphene.Argument(
                              graphene.Int,
                              required=True
                          ))

    users = graphene.Field(graphene.List(types.User), group_id=graphene.Int())

    group = graphene.Field(types.Group,
                           id=graphene.Argument(
                               graphene.Int,
                               required=True
                           ))

    groups = graphene.Field(graphene.List(types.Group), user_id=graphene.Int())

    division = graphene.Field(types.Division, id=graphene.Int())

    divisions = graphene.Field(graphene.List(types.Division))

    permission = graphene.Field(types.Permission,
                                entity_id=graphene.Argument(
                                    graphene.Int,
                                    required=True
                                ),
                                division_id=graphene.Argument(
                                    graphene.Int,
                                    required=True
                                ),
                                permission_type=graphene.Argument(
                                    types.PermissionType,
                                    required=True
                                ))

    permissions = graphene.Field(graphene.List(types.Permission),
                                 entity_id=graphene.Argument(
                                     graphene.Int
                                 ),
                                 division_id=graphene.Argument(
                                     graphene.Int
                                 ),
                                 permission_type=graphene.Argument(
                                     types.PermissionType
                                 ))

    notes = graphene.Field(graphene.List(types.Note),
                           subject_id=graphene.Argument(
                               graphene.Int,
                               required=True
                           ))

    character = graphene.Field(types.Character,
                               id=graphene.Argument(
                                   graphene.Int,
                                   required=True
                               ))

    killmail = graphene.Field(types.Killmail,
                              id=graphene.Argument(
                                  graphene.Int,
                                  required=True
                              ))

    killmails = graphene.Field(graphene.List(types.Killmail),
                               limit=graphene.Int(),
                               after_cursor=graphene.ID(),
                               search=graphene.Argument(
                                   pagination.InputKillmailSearch
                               ),
                               sort=graphene.Argument(
                                   pagination.InputSort
                               ))

    actions = graphene.Field(graphene.List(types.Action),
                             request_id=graphene.Argument(
                                 graphene.Int,
                                 required=True
                             ))

    modifiers = graphene.Field(graphene.List(types.Modifier),
                               request_id=graphene.Argument(
                                   graphene.Int,
                                   required=True
                               ),
                               include_void=graphene.Argument(
                                   graphene.Boolean,
                                   default_value=True,
                               ),
                               modifier_type=graphene.Argument(
                                   types.ModifierType
                               ))

    request = graphene.Field(types.Request,
                             id=graphene.Int(),
                             killmail_id=graphene.Int(),
                             division_id=graphene.Int())

    requests = graphene.Field(pagination.Pager,
                              limit=graphene.Int(),
                              after_cursor=graphene.ID(),
                              search=graphene.Argument(
                                  pagination.InputRequestSearch
                              ),
                              sort=graphene.Argument(
                                  pagination.InputSort
                              ))


schema = graphene.Schema(query=Query)
