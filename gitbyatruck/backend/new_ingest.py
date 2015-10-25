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
    Ingest a patch from a repo and put it into postgres
    """
    if not (patch.additions + patch.deletions):
        return

    session.execute(persist.diffs.insert().values([(
        commit.hex,
        patch.additions,
        patch.deletions,
        patch.new_file_path,
        patch.old_file_path,
        {}
    )]))


async def stat_diff(session, repo, commit):
    """
    Coroutine used in the libgit2 tree walker
    """
    if not commit.parent_ids:
        return False
    log.debug("Parsing commit {0} repo_id={1}".format(
        commit.hex[:8],
        repo.path))
    diff = await create_diff(repo, commit)
    if diff is None:
        return False
    ingest_cr = partial(ingest_patch, session, commit)
    crs = [ingest_cr(patch) for patch in diff]
    await asyncio.gather(*crs)
    return True


async def ingest_repo(session, repo, clone_url):
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    stat_cr = partial(stat_diff, session, repo)  # Partial for the stat_diff function
    crs = [stat_cr(commit) for commit in walker]  # Create a bunch of corountines
    start_time = time.time()
    count = 0
    await asyncio.gather(*crs)  # wait for our coroutines to finish
    end_time = time.time()
    logging.info("Ingested {0} commits from '{1}' in {2} seconds".format(
        count,
        repo.path,
        end_time - start_time))
