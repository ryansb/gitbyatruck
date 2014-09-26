from pyramid.response import Response
from pyramid.view import view_config

from gitbyatruck.models import (
    DBSession,
    Repository,
    )


@view_config(route_name='home', renderer='gitbyatruck:templates/home.pt')
def home(request):
    repos = DBSession.query(Repository).all()
    return {'title': 'Welcome to gitbyatruck',
            'repos': repos,
            'project': 'gitbyatruck'}
