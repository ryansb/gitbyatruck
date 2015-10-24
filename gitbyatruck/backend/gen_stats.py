# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


import logging
from time import time

import pygit2
from progressbar import ProgressBar
from progressbar.widgets import Bar, Percentage, Timer

from gitbyatruck.models import Change
from gitbyatruck import persist
from gitbyatruck.backend.interesting import interest_callable
from gitbyatruck.model_helpers import author_id, repo_id, _fullname


log = logging.getLogger(__name__)

DBSession = None


def stat_diff(repo, commit, clone_url, session, fname_filter=interest_callable()):
    """
    repo: libgit2 repo object
    commit: commit
    clone_url: clone URL for the repo, used as pkey for repos
    """
    if not commit.parent_ids:
        return
    short = commit.hex
    log.debug("Parsing commit {} repo_id={}".format(short, rid))
    try:
        diff = repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except:
        print("Problem diffing {} against its parents. {}".format(
            commit.hex, commit.parent_ids))
        return

    author = author_id(_fullname(commit.author), rid)

    patches = []
    for patch in diff:
        if not (patch.additions or patch.deletions):
            continue
        if patch.new_file_path != patch.old_file_path:
            print("Path change! we don't handle those")

        path = patch.new_file_path or patch.old_file_path

        if fname_filter is not None and fname_filter(path) is False:
            # bail if the file isn't one we care about
            continue
        # otherwise keep going
        patches.append(
            (
                short,
                patch.additions,
                patch.deletions,
                patch.new_file_path,
                patch.old_file_path,
                {}
            )
        )

    session.execute(persist.diffs.insert().values(patches))



def hex_generator(repo):
    w = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    for c in w:
        yield c.hex


def ingest_repo(repo, verbose=False, suffixes=None, session=None):
    global DBSession
    DBSession = session

    count = 0
    if verbose:
        for _ in repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME):
            count += 1

    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    bar = ProgressBar(maxval=count, widgets=[Percentage(),
                                             ' ',
                                             Bar(),
                                             ' ',
                                             Timer()]
                      )

    verbose and bar.start()
    interval_seconds = 90
    flush_after = time() + interval_seconds
    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(repo.path[:-6]),
                  fname_filter=interest_callable(suffixes=suffixes)
                  )
        if time() > flush_after:
            DBSession.flush()
            flush_after = time() + interval_seconds
        verbose and bar.update(bar.currval + 1)
    DBSession.flush()

    verbose and bar.finish()


def ingest_worker(repo, clone_url):
    """Same as `ingest` but without progress bar"""
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    log.info("Ingestion request for {} received".format(clone_url))

    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(clone_url),
                  )
