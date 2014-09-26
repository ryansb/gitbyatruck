from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from gitbyatruck.models import (
    DBSession,
    Repository,
    )


@view_config(route_name='addrepo', renderer='gitbyatruck:templates/repos.pt')
def add_repo(request):
    return {'title': 'RULE', 'one': 'one', 'project': 'gitbyatruck'}
