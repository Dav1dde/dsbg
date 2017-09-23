from __future__ import unicode_literals

import datetime
import hashlib
import os.path
import re

# fix mardkown regex
import markdown.util
from jinja2 import Environment, FileSystemLoader

import dsbg.ext.voltlexer  # import it, so the lexer is registered
from dsbg.content import Site, Post, Other
from dsbg.generator import GENERATORS
from dsbg.writer import Writer
import dsbg.util

markdown.util.BLOCK_LEVEL_ELEMENTS = re.compile(
    r'^(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul'
    r'|script|noscript|form|fieldset|iframe|math'
    r'|hr|hr/|style|li|dt|dd|thead|tbody'
    r'|tr|th|td|section|footer|header|group|figure'
    r'|figcaption|aside|article|canvas|output'
    r'|progress|video|nav)$', re.IGNORECASE
)


class DSBG(object):
    def __init__(self, settings):
        self.settings = settings
        self.settings['url'] = self.settings['url'].strip().rstrip('/')

        self.path = settings['path']
        self.output_path = settings['output_path']

    def run(self):
        posts, sites, other, environment = self.gather()
        writer = Writer(self.output_path,
            _posts=posts, _sites=sites, _other=other, _settings=self.settings
        )

        generators = [
            cls(
                self.settings,
                environment,
                writer,
                posts,
                sites
            ) for cls in GENERATORS
        ]

        for generator in generators:
            generator.run()

    def gather(self):
        posts = sorted([
            Post(
                os.path.join(os.path.join(self.path, 'posts'), f)
            ) for f in dsbg.util.listdir_safe(os.path.join(self.path, 'posts'))
        ], key=lambda x: x.date, reverse=True)

        sites = [
            Site(
                os.path.join(os.path.join(self.path, 'sites'), f)
            ) for f in dsbg.util.listdir_safe(os.path.join(self.path, 'sites'))
        ]

        other = dict(
            (
                os.path.splitext(f)[0],
                Other(
                    os.path.join(os.path.join(self.path, 'other'), f)
                ),
            ) for f in dsbg.util.listdir_safe(os.path.join(self.path, 'other'))
        )

        environment = Environment(
            loader=FileSystemLoader(
                os.path.join(
                    self.path,
                    'themes',
                    self.settings['theme'],
                    'templates'
                )
            )
        )

        environment.filters['ordinal'] = (lambda x:
            'th' if 11 <= x <= 13 else {1: 'st',2: 'nd',3: 'rd'}.get(x % 10, 'th')
        )
        environment.filters['md5'] = lambda x: hashlib.md5(x).hexdigest()
        environment.filters['iso8601'] = (lambda obj:
            obj.strftime('%Y-%m-%dT%H:%M:%S' + self.settings.get('timezone', 'Z'))
        )

        environment.globals['now'] = datetime.datetime.utcnow()
        
        return posts, sites, other, environment