# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import click
import pygit2
import sqlalchemy

from gitbyatruck import persist
from gitbyatruck.models import DBSession
from gitbyatruck.backend.gen_stats import ingest_repo
from gitbyatruck.scripts.initializedb import main as db_init


@click.group()
def cli():
    pass

connection_string = 'postgres:///example'

@cli.command(short_help="Destroy database")
@click.option("--config", default="./development.ini", help="Path to ini file")
def clean(config):
    db = sqlalchemy.create_engine(connection_string)
    engine = db.connect()
    persist.metadata.bind = engine
    persist.metadata.drop_all()
    persist.metadata.create_all()
    click.echo(u'\u2714 Dropped and recreated tables')


@cli.command(short_help="Make a new course site from scratch")
@click.option("--repo-path", help="Path to repo")
@click.option("--config", default="./development.ini", help="Path to ini file")
@click.option("--progress", is_flag=True,
              help="Show progress bar")
@click.option("--drop", is_flag=True,
              help="Drop and recreate tables")
@click.option("--no-stats", is_flag=True,
              help="Skip calculating stats")
@click.option("--no-ingest", is_flag=True, help="Skip ingesting the repo")
def run(repo_path, drop, no_ingest, no_stats, progress, config, suffixes):
    settings = get_appsettings(config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    if drop:
        db_init(['foo', config])
        click.echo(u'\u2714 Dropped and recreated tables')

    if not repo_path:
        repo_path = '/home/ryansb/code/hflossk/'

    repo = pygit2.init_repository(repo_path)

    # \u2714 is a check mark
    # \u2717 is an x
    click.echo(u'\u2714 Opened repository')

    if no_ingest:
        click.echo(u'\u2717 skipped ingestion')
    else:
        click.echo(u'\u2714 reading stats')
        ingest_repo(repo,
                    verbose=progress,
                    suffixes=suffixes,
                    session=create_session(bind=engine),
                    )
        click.echo(u'\u2714 ingested repo stats')

    if no_stats:
        return

    click.echo(u'\u2714 first knowledge estimate complete')
