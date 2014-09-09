# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import pygit2

from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gitbyatruck.models import Committer, File, Repository, Change

_engine = create_engine('postgres://gitter@127.0.0.1/tgit')
Session = sessionmaker(bind=_engine)


def stat_diff(repo, commit, rid, session=None):
    if not commit.parent_ids:
        return
    short = commit.hex[:8]
    diff = None
    try:
        diff = repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except Exception as e:
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
            short_hash=short,
            changed_file=fid,
            committer=author,
            added=patch.additions,
            deleted=patch.deletions)
        session.add(c)
    session.commit()


def _fullname(author):
    return "{} <{}>".format(
        author.name,
        author.email,
    )


@lru_cache(maxsize=4096)
def author_id(session, fullname):
    return _find_or_create_author(session, fullname).id


def _find_or_create_author(session, fullname):
    user = session.query(Committer).filter_by(name=fullname).first()
    if not user:
        user = Committer()
        user.name = fullname
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@lru_cache(maxsize=8192)
def file_id(session, name, rid):
    f = find_or_create_file(session, name, rid)
    return f.id


def find_or_create_file(session, name, rid):
    f = session.query(File).filter_by(name=name, repo=rid).first()
    if not f:
        f = File()
        f.repo = rid
        f.name = name
        session.add(f)
        session.commit()
        session.refresh(f)
    return f


@lru_cache(maxsize=32)
def repo_id(session, name):
    repo = find_or_create_repo(session, name)
    return repo.id


def find_or_create_repo(session, name):
    repo = session.query(Repository).filter_by(name=name).first()
    if not repo:
        repo = Repository()
        repo.name = name
        session.add(repo)
        session.commit()
        session.refresh(repo)
    return repo


def hex_generator(repo):
    w = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    for c in w:
        yield c.hex


def stats_for_repo(repo):
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    session = Session()

    for commit in walker:
        stat_diff(repo, commit, rid=repo_id(session, repo.path[:-6]), session=session)
