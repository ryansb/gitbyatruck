# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import click
import pygit2

from gitbyatruck.gen_stats import ingest_repo
from gitbyatruck.models import create_tables


@click.group()
def cli():
    pass


@cli.command(short_help="Destroy database")
def clean():
    create_tables()
    click.echo(u'\u2714 Dropped and recreated tables')


@cli.command(short_help="Make a new course site from scratch")
@click.option("--repo-path", help="Path to repo")
@click.option("--drop", is_flag=True,
              help="Drop and recreate tables")
@click.option("--no-stats", is_flag=True,
              help="Skip calculating stats")
@click.option("--no-ingest", is_flag=True, help="Skip ingesting the repo")
def run(repo_path, drop, no_ingest, no_stats):
    if drop:
        create_tables()
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
        ingest_repo(repo)
        click.echo(u'\u2714 ingested repo stats')

    if no_stats:
        return

    click.echo(u'\u2714 first knowledge estimate complete')
