# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

from sqlalchemy import Integer, String, ForeignKey, Column, UnicodeText, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy_utils as sqa_utils


Base = declarative_base()


class Repository(Base):
    __tablename__ = 'repo'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    files = relationship("File")


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    repo = Column(Integer, ForeignKey('repo.id'))
    changes = relationship("Change")
    total_knowledge = Column(Integer)


class Committer(Base):
    __tablename__ = 'committer'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    changes = relationship("Change")


class Change(Base):
    __tablename__ = 'change'
    id = Column(Integer, primary_key=True)
    short_hash = Column(String(8))
    commit_time = Column(Integer)
    changed_file = Column(Integer, ForeignKey('file.id'))
    committer = Column(Integer, ForeignKey('committer.id'))
    added = Column(Integer)
    deleted = Column(Integer)


class Knol(Base):
    __tablename__ = 'knol'
    id = Column(Integer, primary_key=True)
    changed_file = Column(Integer, ForeignKey('file.id'))
    committer = Column(Integer, ForeignKey('committer.id'))
    knowledge = Column(Integer)
    unique = Column(Boolean)


def create_tables():
    url = 'postgres://gitter@127.0.0.1/tgit'

    engine = create_engine(url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine, checkfirst=False)
