from datetime import datetime
import logging
from multiprocessing import Pool
import json

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPAccepted,
    HTTPOk,
    HTTPFound,
    HTTPNotFound,
)

import transaction
import colander

from gitbyatruck.models import (
    Committer,
    DBSession,
    File,
    Knol,
    Repository,
)
from gitbyatruck.backend.worker import background_ingest


log = logging.getLogger(__name__)

pool = Pool()


class NewRepo(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    clone_url = colander.SchemaNode(colander.String())


form_schema = NewRepo()


@view_config(route_name='addrepo',
             renderer='gitbyatruck:templates/git_form.mako')
def add_repo(request):
    return {'title': 'Repositories',
            }


@view_config(route_name='addrepo', renderer='json', request_method='POST')
def start_repo(request):
    log.info("Received request {}".format(json.dumps(request.matchdict)))

    if request.json_body.get('clone_url') is None or (request.json_body.get('name')
                                                 is None):
        raise HTTPBadRequest
    log.info(request.body)


    clone_url = request.json_body.get('clone_url')

    with transaction.manager:
        r = DBSession.query(Repository).filter_by(
            clone_url=request.json_body.get('clone_url')).first()

        if r is not None:
            # TODO: when a repo already exists, fire off a job to pull from it
            # and update stats. For now, whatever.
            return {'link': '/repo/{}'.format(r.id)}

        # The repo hasn't already been cloned, so let's save it.
        r = Repository()

        r.name = request.json_body.get('name')
        r.clone_url = request.json_body.get('clone_url')
        r.created_at = datetime.now()

        DBSession.add(r)

    pool.apply_async(background_ingest, (clone_url,))
    #background_ingest(request.json['clone_url'])

    log.info("Fired async request, done here!")
    with transaction.manager:
        r = DBSession.query(Repository).filter_by(
            clone_url=request.json_body.get('clone_url')).first()
        return HTTPFound(request.route_url('jsonstats', id=r.id))

    raise HTTPAccepted


@view_config(route_name='jsonstats',
             renderer='json')
def jsonify_stats(request):
    repo = DBSession.query(Repository).filter(
        Repository.id == request.matchdict['id']).first()
    if repo is None:
        log.info("Could not find repo with ID {}".format(
            request.matchdict['repo_id']))
        raise HTTPNotFound

    resp = {}
    resp['name'] = repo.name
    resp['clone_url'] = repo.clone_url

    if repo.ingest_begun_at:
        if repo.ingest_finished_at:
            # how long did the job take?
            runtime = repo.ingest_finished_at - repo.ingest_begun_at
        else:
            # or how long has the job been running
            runtime = datetime.now() - repo.ingest_begun_at
        resp['run_seconds'] = runtime.seconds

    if repo.ingest_finished_at:
        resp['finished'] = True
    else:
        resp['finished'] = False
        # No stats, bail out.
        return resp

    resp['stats'] = _stat_repo(repo.id)
    #don't forget to jsonify it
    return json.dumps(resp)

def _stat_repo(rid):
    knowledge = DBSession.query(
        Knol.knowledge,
        Committer.name,
        File.name,
        Knol.repo,
    ).join(
        Committer,
        Knol.committer == Committer.id,
    ).join(
        File,
        Knol.changed_file == File.id,
    ).filter(
        Knol.repo == rid
    ).all()

    stats = {}

    for knol in knowledge:
        listing = stats.get(knol[2], [])
        listing.append({'k': knol[0], 'c': knol[1]})
        stats[knol[2]] = listing
    return stats


@view_config(route_name='viewstats',
             renderer='gitbyatruck:templates/display_repo_stats.mako')
def view_repo(request):
    repo = DBSession.query(Repository).filter(
        Repository.id == request.matchdict['repo_id']).first()
    if repo is None:
        log.info("Could not find repo with ID {}".format(
            request.matchdict['repo_id']))
        raise HTTPNotFound
    resp = {'repo': repo, 'stats': _stat_repo(repo.id)}
    return resp
