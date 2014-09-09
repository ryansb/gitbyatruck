# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import click
import pygit2

from gitbyatruck.gen_stats import stats_for_repo
from gitbyatruck.models import create_tables


@click.group()
def cli():
    pass


@cli.command(short_help="Make a new course site from scratch")
@click.option("--repo-path", help="Path to repo")
@click.option("--drop", is_flag=True, help="Drop the tables like a pound of bacon")
def new(repo_path, drop):
    if drop: create_tables()
    # \u2714 is a check mark
    # \u2717 is an x
    click.echo(u'\u2714 WOOO')
    if not repo_path:
        repo_path = '/home/ryansb/code/hflossk/'

    repo = pygit2.init_repository(repo_path)
    stats_for_repo(repo)

if __name__ == "__main__":
    new("")
