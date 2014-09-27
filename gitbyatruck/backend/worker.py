# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

from datetime import datetime
import os
import uuid

import pygit2
import transaction

from gitbyatruck.models import DBSession, Repository
from gitbyatruck.backend.gen_stats import ingest_worker


def temp_path(root):
    if not os.path.isdir(root):
        os.makedirs(root)

    return os.path.join(
        root,
        str(uuid.uuid4()).replace('-', '')[:10],
    )


def clone_repo(repo_model, session):
    repo = pygit2.clone_repository(
        url=repo_model.clone_url,
        path=repo_model.disk_path,
        bare=True,
    )
    ingest_worker(repo, session)


def sanitize_url(orig):
    # TODO: actually do a thing here
    return orig


def async_ingest(name):
    session = DBSession()
    repo_model = session.query(Repository).filter_by(name=name).first()
    fpath = temp_path('/tmp/gitbyatruck-data')
    repo_model.clone_url = sanitize_url(repo_model.clone_url)
    repo_model.disk_path = fpath
    repo_model.ingest_begun_at = datetime.now()
    transaction.commit()
    clone_repo(repo_model, session)
    repo_model.ingest_finished_at = datetime.now()
    transaction.commit()
