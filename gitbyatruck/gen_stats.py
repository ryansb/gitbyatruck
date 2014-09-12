# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3


import pygit2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gitbyatruck.models import Change, File, Knol, Base
from gitbyatruck.model_helpers import author_id, file_id, repo_id, _fullname

_engine = create_engine('postgres://gitter@127.0.0.1/tgit')
Session = sessionmaker(bind=_engine)


def stat_diff(repo, commit, rid, session=None):
    if not commit.parent_ids:
        return
    short = commit.hex[:8]
    diff = None
    try:
        diff = repo.diff(commit.hex, commit.hex + '^', context_lines=0)
    except:
        print("Problem diffing {} against its parents. {}".format(
            commit.hex, commit.parent_ids))
        return

    if session is None:
        session = Session()
    author = author_id(session, _fullname(commit.author))
    for patch in diff:
        if not (patch.additions + patch.deletions):
            continue
        if patch.new_file_path != patch.old_file_path:
            print("Path change! we don't handle those")
        path = patch.new_file_path or patch.old_file_path
        fid = file_id(session, path, rid)

        c = Change(
            short_hash=short,
            changed_file=fid,
            commit_time=commit.commit_time,
            committer=author,
            added=patch.additions,
            deleted=patch.deletions)
        session.add(c)
    session.commit()


def hex_generator(repo):
    w = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    for c in w:
        yield c.hex


def ingest_repo(repo):
    walker = repo.walk(repo.head.get_object().hex, pygit2.GIT_SORT_TIME)
    session = Session()

    for commit in walker:
        stat_diff(repo,
                  commit,
                  rid=repo_id(session, repo.path[:-6]),
                  session=session,
                  )


CHURN_CONSTANT = 0.1


def knowledge_estimate(repo):
    session = Session()
    rid = repo_id(session, repo.path[:-6])
    files = session.query(File).all()
    for f in files:
        file_knowledge(f, session)

def file_knowledge(f, session):
    changes = session.query(
        Change
    ).filter_by(
        changed_file=f.id
    ).order_by(
        Change.commit_time
    )

    for c in changes.all():
        # calculate the stuff
        adjustment = c.added - c.deleted
        #adjust_file_knowledge(f.id, adjustment)
        churn = min(c.added, c.deleted)
        if adjustment > 0:
            dev_create_unique(f.id, c.committer, adjustment, session)
        elif adjustment < 0:
            destroy_knowledge(f.id, c.committer, adjustment, session)

        new_knowledge = float(churn) * CHURN_CONSTANT
        shared_knowledge = float(churn) - new_knowledge
        #sequential_distribute_shared_knowledge(dev, shared_knowledge, tot_knowledge, dev_uniq)
        #sequential_create_knowledge(dev_uniq, dev, new_knowledge)
        #tot_knowledge += adjustment + (churn * CHURN_CONSTANT)


#def adjust_file_knowledge(fid, adjustment):
#    if adjustment > 0:
#        sequential_create_knowledge(dev_uniq, dev, adjustment)
#    elif adjustment < 0:
#        sequential_destroy_knowledge(adjustment, tot_knowledge, dev_uniq)


def destroy_knowledge(file_id, committer_id, adjustment, session):
    total_knowledge = session.query(Knol).filter_by(
        changed_file=file_id,
        unique=False,
    ).first()
    if total_knowledge:
        knol_pct = abs(float(adjustment) / float(total_knowledge.knowledge))
        session.query(Knol).filter_by(
            changed_file=file_id,
            unique=True,
        ).update(
            {"knowledge": Knol.knowledge * (1 - knol_pct)}
        )


def dev_create_unique(file_id, committer_id, adjustment, session):
    # if we already have a knowledge record for this committer-file combo
    if session.query(Knol).filter_by(
        changed_file=file_id,
        committer=committer_id,
        unique=True,
    ).count():
        session.query(Knol).filter_by(
            unique=True,
            changed_file=file_id,
            committer=committer_id
        ).update(
            {"knowledge": Knol.knowledge + adjustment}
        )
    else:
        k = Knol(
            changed_file=file_id,
            committer=committer_id,
            knowledge=adjustment,
            unique=True,
        )
        session.add(k)
        session.commit()

    if session.query(Knol).filter_by(
        changed_file=file_id,
        unique=False,
    ).count():
        session.query(Knol).filter_by(
            changed_file=file_id,
            unique=False,
        ).update(
            {"knowledge": Knol.knowledge + adjustment}
        )
    else:
        k = Knol(
            changed_file=file_id,
            knowledge=adjustment,
            unique=False,
        )
        session.add(k)
        session.commit()
