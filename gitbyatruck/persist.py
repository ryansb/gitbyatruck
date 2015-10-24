# tables
# commits: hash author committer date parent parents other
# diffs: commit_hash old_name new_name added removed other
# repos: clone_url name
# authors: username display emails
import sqlalchemy
from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON, ARRAY

metadata = sqlalchemy.MetaData()

repos = sqlalchemy.Table(
    "repos", metadata,
    Column('clone_url', Text, primary_key=True),
    Column('name', Text),
    Column('other', JSON))

commits = sqlalchemy.Table(
    "commits", metadata,
    Column('hash', Text, primary_key=True),
    Column('repo_url', Text, ForeignKey(repos.c.clone_url), nullable=False),
    Column('committer_name', Text),
    Column('committer_email', Text, nullable=False),
    Column('author_name', Text),
    Column('author_email', Text),
    Column('commit_date', DateTime),
    Column('author_date', DateTime),
    Column('message', Text),
    Column('is_merge', Boolean),
    Column('parent', Text, nullable=False),
    Column('parents', ARRAY(Text)),
    Column('other', JSON))

diffs = sqlalchemy.Table(
    "diffs", metadata,
    Column('commit_hash', Text, ForeignKey(commits.c.hash), nullable=False),
    Column('added', Integer),
    Column('removed', Integer),
    Column('file_name', Text),
    Column('old_name', Text),
    Column('other', JSON))

authors = sqlalchemy.Table(
    "authors", metadata,
    Column('id', Integer, primary_key=True),
    Column('username', Text, nullable=False),
    Column('display', Text),
    Column('emails', ARRAY(Text)),
    Column('other', JSON))

_tables = [
    repos,
    commits,
    diffs,
    authors,
]
