from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
import deform
import colander

from gitbyatruck.models import (
    DBSession,
    Repository,
    )


class NewRepo(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    clone_url = colander.SchemaNode(colander.String())


form_schema = NewRepo()


@view_config(route_name='addrepo', renderer='gitbyatruck:templates/git_form.mako')
def add_repo(request):
    new_repo_form = deform.Form(form_schema, buttons=('clone it',))
    return {'title': 'Repositories',
            'form': new_repo_form,
            }


