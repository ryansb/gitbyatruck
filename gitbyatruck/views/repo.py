from datetime import datetime
import logging
from multiprocessing import Pool
import json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPAccepted

import transaction
from sqlalchemy.exc import DBAPIError
import deform
import colander

from gitbyatruck.models import (
    DBSession,
    Repository,
    )
from gitbyatruck.backend.worker import background_ingest


log = logging.getLogger(__name__)

pool = Pool()


class NewRepo(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    clone_url = colander.SchemaNode(colander.String())


form_schema = NewRepo()


@view_config(route_name='addrepo', renderer='gitbyatruck:templates/git_form.pt')
def add_repo(request):
    new_repo_form = deform.Form(form_schema, buttons=('clone it',))
    form = new_repo_form.render()
    return {'title': 'Repositories',
            'form': form,
            }


@view_config(route_name='addrepo', renderer='json', request_method='POST')
def start_repo(request):
    log.info("Received request {}".format(json.dumps(request.matchdict)))


    if request.POST.get('clone_url') is None or request.POST.get('name') is None:
        raise HTTPBadRequest
    log.info(request.body)

    r = Repository()

    r.name = request.POST.get('name')
    r.clone_url = request.POST.get('clone_url')
    r.created_at = datetime.now()

    with transaction.manager:
        DBSession.add(r)

    pool.apply_async(background_ingest, (r.clone_url,))
    #background_ingest(request.json['clone_url'])

    log.info("Fired async request, done here!")
    raise HTTPAccepted
