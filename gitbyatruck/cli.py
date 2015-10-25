# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import click
import pygit2
import sqlalchemy
import asyncio

from gitbyatruck import persist
from gitbyatruck.backend.new_ingest import ingest_repo


@click.group()
def cli():
    pass

@cli.command(short_help="Destroy database")
@click.option("--dburi", default="postgres:///example",
              help="Database connection string")
def clean(dburi):
    db = sqlalchemy.create_engine(dburi)
    engine = db.connect()
    persist.metadata.bind = engine
    persist.metadata.drop_all()
    persist.metadata.create_all()
    click.echo(u'\u2714 Dropped and recreated tables')


@cli.command(short_help="Make a new course site from scratch")
@click.option("--repo-path", help="Path to repo")
@click.option("--repo-name", default="test project",
              help="Display name for project")
@click.option("--dburi", default="postgres:///example",
              help="Database connection string")
@click.option("--progress", is_flag=True,
              help="Show progress bar")
@click.option("--drop", is_flag=True,
              help="Drop and recreate tables")
@click.option("--no-stats", is_flag=True,
              help="Skip calculating stats")
@click.option("--no-ingest", is_flag=True, help="Skip ingesting the repo")
def run(repo_path, dburi, drop, no_ingest, no_stats, progress, repo_name):
    loop = asyncio.get_event_loop()
    db = sqlalchemy.create_engine(dburi)
    engine = db.connect()
    persist.metadata.bind = engine

    if drop:
        persist.metadata.drop_all()
        persist.metadata.create_all()
        click.echo(u'\u2714 Dropped and recreated tables')

    if not repo_path:
        repo_path = '/home/ryansb/code/hflossk/'

    clone_url = get_clone_url(repo_path)

    engine.execute(
        persist.repos.insert().values(
            (clone_url, 'test_repo', {})
        )
    )

    repo = pygit2.init_repository(repo_path)

    # \u2714 is a check mark
    # \u2717 is an x
    click.echo(u'\u2714 Opened repository')

    if no_ingest:
        click.echo(u'\u2717 skipped ingestion')
    else:
        click.echo(u'\u2714 reading repository')
        loop.run_until_complete(
            ingest_repo(
                engine,
                repo,
                clone_url,
            )
        )
        click.echo(u'\u2714 ingested repo stats')

    click.echo(u'\u2714 first knowledge estimate complete')
    loop.close()


def get_clone_url(repo_path):
    remote = 'origin'
    import subprocess
    out = subprocess.check_output(['git', 'remote', 'show', remote, '-n'], cwd=repo_path)
    fetch_line = [l for l in out.decode().splitlines() if 'Fetch URL' in l][0]
    return fetch_line.split(':', 1)[-1].strip()
