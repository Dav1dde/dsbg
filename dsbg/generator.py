from __future__ import unicode_literals

from shutil import copytree, rmtree
from datetime import date
import json
import os


class Generator(object):
    def __init__(self, settings, env, writer, posts, sites):
        self.settings = settings
        self.env = env
        self.writer = writer
        self.posts = posts
        self.sites = sites

        self._templates = dict()

    def run(self):
        raise NotImplementedError

    def get_template(self, name):
        if name not in self._templates:
            self._templates[name] = self.env.get_template(name + '.html')

        return self._templates[name]

    def write(self, *args, **kwargs):
        self.writer.write(*args, **kwargs)

    def write_raw(self, path, name, data):
        template = self.get_template('raw')
        self.writer.write(template, {'raw': data}, path, name)

    def copy(self, source, name):
        self.writer.copy(source, name)

    def copy_static(self, base_path, static_files):
        for (source, name) in static_files:
            self.copy(source, os.path.join(base_path, name))


class IndexGenerator(Generator):
    def run(self):
        template = self.get_template('index')

        self.write(template, {'posts': self.posts}, '', 'index.html')


class SiteGenerator(Generator):
    def run(self):
        self.generate_sites()

    def generate_sites(self):
        template = self.get_template('site')
        for site in self.sites:
            self.write(template, {'site': site}, site.path, 'index.html')
            self.write_raw(site.path, site.slug + '.md', site.content)
            self.copy_static(site.static_files)


class PostGenerator(Generator):
    def run(self):
        self.generate_posts()

    def generate_posts(self):
        template = self.get_template('post')
        for post in self.posts:
            self.write(template, {'post': post}, post.path, 'index.html')
            self.write_raw(post.path, post.slug + '.md', post.content)
            self.copy_static(post.path, post.static_files)


class StaticGenerator(Generator):
    def run(self):
        rmtree(os.path.join(self.writer.output_path, 'static'), True)
        copytree(
            os.path.join(self.settings['path'], 'themes',
                         self.settings['theme'], 'static'),
            os.path.join(self.writer.output_path, 'static')
        )


class JSONGenerator(Generator):
    def run(self):
        template = self.get_template('raw')

        j = {
            'posts': [post.data for post in self.posts],
            'sites': [site.data for site in self.sites]
        }

        def extended_json(obj):
            if isinstance(obj, date):
                return {'day': obj.day, 'month': obj.month, 'year': obj.year}
            return obj

        self.write_raw('', 'information.json', json.dumps(j, default=extended_json))


class FeedGenerator(Generator):
    def run(self):
        template = self.get_template('feed')

        self.write(template, {}, '', 'atom.xml')


GENERATORS = [
    IndexGenerator, SiteGenerator, PostGenerator,
    StaticGenerator, JSONGenerator, FeedGenerator
]