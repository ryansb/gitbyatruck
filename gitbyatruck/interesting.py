# -*- coding; utf-8 -*-
# Author: Ryan Brown <sb@ryansb.com>
# License: Affero GPLv3

import re

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

    fname_filters.append(re.compile('|'.join([s + '$' for s in suffixes])))

    if prefixes is not None:
        fname_filters.append(re.compile('|'.join(['^' + p for p in prefixes])))

    if regexes is not None:
        fname_filters.extend([re.compile(r) for r in regexes])

    def checkfile(fname):
        for f in fname_filters:
            if r.match(fname):
                return True
        return False

    return checkfile
