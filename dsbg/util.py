from __future__ import unicode_literals

import os
import re
from unicodedata import normalize
from datetime import date


def date_from_string(inp):
    return date(*map(int, inp.split('.')))


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def listdir_safe(path):
    try:
        return os.listdir(path)
    except OSError:
        return []


def listdir_fullpath(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory)]
