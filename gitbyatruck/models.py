# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Repository(Base):
    __tablename__ = 'repo'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    clone_url = Column(String(511), unique=True)
    disk_path = Column(String(511), unique=True)
    created_at = Column(DateTime())
    ingest_finished_at = Column(DateTime())
    files = relationship("File")


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    repo = Column(Integer, ForeignKey('repo.id'))
    total_knowledge = Column(Integer)


class Committer(Base):
    __tablename__ = 'committer'
    id = Column(Integer, primary_key=True)
    repo = Column(Integer, ForeignKey('repo.id'))
    name = Column(String(255), unique=True)
    changes = relationship("Change")


class Change(Base):
    __tablename__ = 'change'
    id = Column(Integer, primary_key=True)
    repo = Column(Integer, ForeignKey('repo.id'))
    short_hash = Column(String(8))
    commit_time = Column(Integer)
    changed_file = Column(String(1024))
    committer = Column(Integer, ForeignKey('committer.id'))
    added = Column(Integer)
    deleted = Column(Integer)


class Knol(Base):
    __tablename__ = 'knol'
    id = Column(Integer, primary_key=True)
    repo = Column(Integer, ForeignKey('repo.id'))
    changed_file = Column(Integer, ForeignKey('files.id'))
    committer = Column(Integer, ForeignKey('committer.id'))
    knowledge = Column(Float)
