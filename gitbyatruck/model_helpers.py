# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


import logging
from functools import lru_cache
import transaction

from gitbyatruck.models import Committer, File, Repository, DBSession


log = logging.getLogger(__name__)


def _fullname(author):
    return "{} <{}>".format(
        author.name,
        author.email,
    )


@lru_cache(maxsize=4096)
def author_id(fullname, rid):
    return _find_or_create_author(fullname, rid).id


def _find_or_create_author(fullname, rid):
    user = DBSession.query(Committer).filter(
        Committer.name == fullname).first()
    if user:
        return user
    with transaction.manager:
        user = Committer()
        user.name = fullname
        user.repo = rid
        DBSession.add(user)
    return DBSession.query(Committer).filter(
        Committer.name == fullname,
        Committer.repo == rid).first()


@lru_cache(maxsize=8192)
def file_id(name, rid):
    log.debug("looking for file {}".format(name))
    f = find_or_create_file(name, rid)
    return f.id


def find_or_create_file(name, rid):
    f = DBSession.query(File).filter(
        File.name == name,
        File.repo == rid,
    ).first()
    if f:
        return f
    with transaction.manager:
        f = File()
        f.repo = rid
        f.name = name
        DBSession.add(f)

    return DBSession.query(File).filter_by(name=name, repo=rid).first()


@lru_cache(maxsize=32)
def repo_id(clone_url):
    repo = find_or_create_repo(clone_url)
    return repo.id


def find_or_create_repo(clone_url):
    repo = DBSession.query(Repository).filter(
        Repository.clone_url == clone_url).first()
    if repo:
        return repo
    with transaction.manager:
        repo = Repository()
        repo.clone_url = clone_url
        DBSession.add(repo)

    return DBSession.query(Repository).filter(
        Repository.clone_url == clone_url).first()
