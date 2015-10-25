# -*- coding; utf-8 -*-
import asyncio
import sqlalchemy
from datetime import datetime
import logging
import pygit2
import time
from functools import partial
from gitbyatruck import persist


log = logging.getLogger(__name__)


async def create_diff(repo, commit):
    """
    Coroutine to return the diffs of this repo. Returns None if repo.diff fails
    """
    try:
        return repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except:
        log.warn("Problem diffing {0} against its parents. {}".format(
            commit.hex, commit.parent_ids))
        return None

async def stat_commit(session, repo, clone_url, commit):
    """
    repo: libgit2 repo object
    commit: commit
    clone_url: clone URL for the repo, used as pkey for repos
    """
    if not commit.parent_ids:
        return
    short = commit.hex[8:]
    commit_id = commit.hex

    c = persist.Commit(
        hash=commit_id,
        repo_url=clone_url,
        committer_name=commit.committer.name,
        committer_email=commit.committer.email,
        commit_date=datetime.fromtimestamp(commit.committer.time + commit.committer.offset * 60),
        author_name=commit.committer.name,
        author_email=commit.committer.email,
        author_date=datetime.fromtimestamp(commit.author.time + commit.author.offset * 60),
        message=commit.message.strip(),
        is_merge=len(commit.parent_ids) > 1,
        parent=commit.parent_ids[0].hex,
        parents=[i.hex for i in commit.parent_ids],
        other={}
    )
    session.execute(persist.commits.insert().values(c))

    log.debug("Parsing commit {}".format(short))
    diff = await create_diff(repo, commit)
    if diff is None:
        return False

    patches = []
    for patch in diff:
        stats = persist.LineStats(*patch.line_stats)
        if not (stats.added or stats.deleted):
            continue

        # otherwise keep going
        patches.append(
            persist.Diff(
                commit_id,
                stats.added,
                stats.deleted,
                patch.delta.new_file.path,
                patch.delta.old_file.path,
                {},
            )
        )
    if len(patches):
        session.execute(persist.diffs.insert().values(patches))

async def ingest_repo(session, repo, clone_url):
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    stat_cr = partial(stat_commit, session, repo, clone_url)  # Partial for the stat_commit function
    crs = [stat_cr(commit) for commit in walker]  # Create a bunch of corountines
    start_time = time.time()
    count = 0
    await asyncio.gather(*crs)  # wait for our coroutines to finish
    end_time = time.time()
    logging.info("Ingested {0} commits from '{1}' in {2} seconds".format(
        count,
        repo.path,
        end_time - start_time))
