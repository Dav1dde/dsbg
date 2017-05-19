from __future__ import unicode_literals

import codecs
import os.path
from hashlib import md5
from datetime import date

import markdown

from dsbg.summary import SummaryExtension
from dsbg.util import slugify, date_from_string

def split_header(f):
    header = dict()

    position = 0
    line = f.next()
    while line.startswith('!'):
        position += len(line)
        data = filter(bool, map(unicode.strip, line.lstrip('!').split(':', 1)))
        header[data[0]] = data[1]
        line = f.next()
    f.seek(position)

    return header, f.read()

class Content(object):
    requires_fields = []

    def __init__(self, path):
        self.parser = markdown.Markdown(
            output_format='html5',
            extensions=[
                'toc', 'codehilite', SummaryExtension()
            ],
            extension_configs = {}
        )

        self._content = ''
        self.html = ''
        self.html_summary = ''
        self.has_summary = False
        self.toc = ''

        try:
            with codecs.open(path, 'r') as f:
                header, self.content = split_header(f)

            for name, func in self.requires_fields:
                setattr(self, name, func(header[name]))
        except (ValueError, StopIteration) as e:
            raise ValueError(
                'Invalid Header in File: "{}", "{}"'.format(path, e.message)
            )
        except KeyError as e:
            raise ValueError(
                'Invalid Header in File: "{}", missing field "{}"'
                    .format(path, e.message)
            )

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, x):
        self.html = self.parser.convert(x)
        self.html_summary = self.parser.summary
        self.has_summary = self.parser.is_summarized
        self.toc = self.parser.toc
        self.parser.reset()

        self._content = x


    @property
    def data(self):
        data = {
            'title': self.title,
            'slug' : self.slug,
            'url': self.url,
        }

        for key, _ in self.requires_fields:
            data[key] = getattr(self, key)

        return data

    @property
    def slug(self):
        return slugify(self.title)


class Post(Content):
    requires_fields = [
        ('title', unicode),
        ('author', unicode),
        ('date', date_from_string)
    ]

    @property
    def path(self):
        return os.path.join(
            'posts',
            self.date.isoformat(),
            self.slug,
            'index.html'
        )

    @property
    def url(self):
        return '/'.join([
            'posts',
            self.date.isoformat(),
            self.slug
        ])


class Site(Content):
    requires_fields = []

    def __init__(self, path):
        Content.__init__(self, path)
        self.title = os.path.splitext(os.path.split(path)[1])[0]

        if self.title in ('static', 'posts'):
            raise ValueError('Invalid site title "{}"'.format(self.title))

    @property
    def path(self):
        return os.path.join(self.slug, 'index.html')

    @property
    def url(self):
        return self.slug


class Other(Content):
    requires_fields = []