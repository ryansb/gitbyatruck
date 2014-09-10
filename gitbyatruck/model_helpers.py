# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


from functools import lru_cache

from gitbyatruck.models import Committer, File, Repository


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


