# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


import pygit2
import logging

from progressbar import ProgressBar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import transaction

from gitbyatruck.models import Change, DBSession
from gitbyatruck.backend.interesting import interest_callable
from gitbyatruck.model_helpers import author_id, file_id, repo_id, _fullname


log = logging.getLogger(__name__)


def stat_diff(repo, commit, rid, fname_filter=interest_callable()):
    if not commit.parent_ids:
        return
    short = commit.hex[:8]
    log.debug("Parsing commit {} repo_id={}".format(short, rid))
    diff = None
    try:
        diff = repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except:
        print("Problem diffing {} against its parents. {}".format(
            commit.hex, commit.parent_ids))
        return

    author = author_id(_fullname(commit.author), rid)
    with transaction.manager:
        for patch in diff:
            if not (patch.additions + patch.deletions):
                continue
            if patch.new_file_path != patch.old_file_path:
                print("Path change! we don't handle those")

            path = patch.new_file_path or patch.old_file_path

            if fname_filter is not None and fname_filter(path) is False:
                # bail if the file isn't one we care about
                continue
            # otherwise keep going

            fid = file_id(path, rid)

            c = Change(
                # non unique. One change object per file changed in a commit
                short_hash=short,
                repo=rid,
                changed_file=fid,
                commit_time=commit.commit_time,
                committer=author,
                added=patch.additions,
                deleted=patch.deletions)
            DBSession.add(c)


def hex_generator(repo):
    w = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    for c in w:
        yield c.hex


def ingest_repo(repo):
    count = 0
    # walker has no len() :(
    for _ in repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME):
        count += 1

    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    session = DBSession()
    bar = ProgressBar(maxval=count)

    bar.start()
    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(session, repo.path[:-6]),
                  )
        bar.update(bar.currval + 1)
    bar.finish()


def ingest_worker(repo, clone_url):
    """Same as `ingest` but without progress bar"""
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    log.info("Ingestion request for {} received".format(clone_url))

    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(clone_url),
                  )
