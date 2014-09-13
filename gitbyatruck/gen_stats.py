# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


import pygit2

from progressbar import ProgressBar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gitbyatruck.models import Change
from gitbyatruck.model_helpers import author_id, file_id, repo_id, _fullname

_engine = create_engine('postgres://gitter@127.0.0.1/tgit')
Session = sessionmaker(bind=_engine)


def stat_diff(repo, commit, rid, session=None):
    if not commit.parent_ids:
        return
    short = commit.hex[:8]
    diff = None
    try:
        diff = repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except:
        print("Problem diffing {} against its parents. {}".format(
            commit.hex, commit.parent_ids))
        return

    if session is None:
        session = Session()
    author = author_id(session, _fullname(commit.author))
    for patch in diff:
        if not (patch.additions + patch.deletions):
            continue
        if patch.new_file_path != patch.old_file_path:
            print("Path change! we don't handle those")
        path = patch.new_file_path or patch.old_file_path
        fid = file_id(session, path, rid)

        c = Change(
            # non unique. One change object per file changed in a commit
            short_hash=short,
            changed_file=fid,
            commit_time=commit.commit_time,
            committer=author,
            added=patch.additions,
            deleted=patch.deletions)
        session.add(c)
    session.commit()


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
    session = Session()
    bar = ProgressBar(maxval=count)

    bar.start()
    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(session, repo.path[:-6]),
                  session=session,
                  )
        bar.update(bar.currval + 1)
    bar.finish()
