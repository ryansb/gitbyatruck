# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import os

from sqlalchemy import (Boolean,
                        Column,
                        DateTime,
                        Float,
                        ForeignKey,
                        Integer,
                        String,
                        text,
                        )
from sqlalchemy import create_engine
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
    name = Column(String(255), unique=True)
    clone_url = Column(String(511), unique=True)
    disk_path = Column(String(511), unique=True)
    created_at = Column(DateTime())
    ttl = Column(Integer) # TTL in hours
    files = relationship("File")


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024), unique=True)
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
    knowledge = Column(Float)
    individual = Column(Boolean)


def create_tables(url):
    engine = create_engine(url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine, checkfirst=False)

    # load procedures
    procedure = os.path.join(
        os.path.split(__file__)[0],
        'procedures',
        'calculate_knowledge.sql',
    )
    with open(procedure, 'r') as p:
        proc = text(p.read())
        engine.execute(proc)
