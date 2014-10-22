import os
import sys

from sqlalchemy import engine_from_config, text

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from gitbyatruck.models import (
    DBSession,
    Base,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    # load procedures
    prefix = os.path.join(
        os.path.split(__file__)[0],
        '..',
        'backend',
        'procedures'
    )
    files = ['churn_knowledge.sql', 'calculate_knowledge.sql']
    for f in files:
        with open(os.path.join(prefix, f), 'r') as p:
            procedure = text(p.read())
            engine.execute(procedure)
