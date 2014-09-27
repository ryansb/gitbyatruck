# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

from datetime import datetime
import logging
import os
import uuid

import pygit2
import transaction

from gitbyatruck.models import DBSession, Repository
from gitbyatruck.backend.gen_stats import ingest_worker


log = logging.getLogger(__name__)


def temp_path(root):
    if not os.path.isdir(root):
        os.makedirs(root)

    return os.path.join(
        root,
        str(uuid.uuid4()).replace('-', '')[:10],
    )


def clone_repo(repo_model, session):
    log.info("Cloning repo name={name} path={path} clone_url={url}".format(
        name=repo_model.name,
        path=repo_model.disk_path,
        url=repo_model.clone_url)
    )
    repo = pygit2.clone_repository(
        url=repo_model.clone_url,
        path=repo_model.disk_path,
        bare=True,
    )
    log.info("Clone successful for {}".format(repo.clone_url))
    ingest_worker(repo, session)
    log.info("Completed repo {}".format(repo.clone_url))


def sanitize_url(orig):
    # TODO: actually do a thing here
    return orig


def async_ingest(name):
    session = DBSession()
    repo_model = session.query(Repository).filter_by(name=name).first()
    log.info("Starting repo name {}".format(name))
    fpath = temp_path('/tmp/gitbyatruck-data')
    repo_model.clone_url = sanitize_url(repo_model.clone_url)
    repo_model.disk_path = fpath
    fpath = temp_path('/tmp/gitbyatruck-data')
    log.info("Ingesting repo name {}".format(name))
    repo_model.ingest_begun_at = datetime.now()
    transaction.commit()
    clone_repo(repo_model, session)
    repo_model.ingest_finished_at = datetime.now()
    transaction.commit()
