# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import re
import logging


log = logging.getLogger(__name__)


def interest_callable(suffixes=None, prefixes=None, regexes=None):
    if suffixes is None:
        suffixes = [
            ".c",
            ".cc",
            ".cpp",
            ".css",
            ".go",
            ".h",
            ".hs",
            ".html",
            ".java",
            ".js",
            ".less",
            ".mak",
            ".php",
            ".pl",
            ".py",
            ".r",
            ".rb",
            ".sass",
            ".sh",
            ".zsh",
        ]

    fname_filters = []

    fname_filters.append(re.compile('.*(' + '|'.join(suffixes) + ')$'))

    if prefixes is not None:
        fname_filters.append(re.compile('^(' + '|'.join(prefixes) + ').*'))

    if regexes is not None:
        fname_filters.extend([re.compile(r) for r in regexes])

    def checkfile(fname):
        for f in fname_filters:
            if f.match(fname):
                return True
        log.info("Failed to match on file {}".format(fname))
        return False

    return checkfile
