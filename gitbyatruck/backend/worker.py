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


def clone_repo(clone_url, path):
    log.info("Cloning repo path={path} clone_url={url}".format(
        path=path,
        url=clone_url)
    )
    repo = pygit2.clone_repository(
        url=clone_url,
        path=path,
        bare=True,
    )
    log.info("Clone successful for {}".format(clone_url))
    session = DBSession()
    ingest_worker(repo, session)
    log.info("Completed repo {}".format(clone_url))


def sanitize_url(orig):
    # TODO: actually do a thing here
    return orig


def background_ingest(clone_url):
    with transaction.manager:
        repo_model = DBSession.query(Repository).filter_by(
            clone_url=clone_url).first()

        if repo_model is None:
            log.warning("Could not retrieve repo {}, bailing "
                        "out".format(clone_url))

        log.info("Starting repo name {}".format(clone_url))
        fpath = temp_path('/tmp/gitbyatruck-data')
        repo_model.clone_url = sanitize_url(repo_model.clone_url)
        repo_model.disk_path = fpath
        fpath = temp_path('/tmp/gitbyatruck-data')
        log.info("Ingesting repo name {}".format(clone_url))
        repo_model.ingest_begun_at = datetime.now()

    clone_repo(clone_url, fpath)
    with transaction.manager:
        repo_model = DBSession.query(Repository).filter_by(
            clone_url=clone_url).first()
        repo_model.ingest_finished_at = datetime.now()
        transaction.commit()
