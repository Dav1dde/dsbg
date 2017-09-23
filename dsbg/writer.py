from __future__ import unicode_literals

import os

import shutil


class Writer(object):
    def __init__(self, output_path, **kwargs):
        self.output_path = output_path
        self.kwargs = kwargs

    def write(self, template, context, path, name):
        lcontext = self.kwargs.copy()
        lcontext.update(context.copy())

        output = template.render(**lcontext)

        path = os.path.join(self.output_path, path, name)
        head, tail = os.path.split(path)
        if not os.path.exists(head):
            os.makedirs(head)

        with open(path, 'w') as f:
            f.write(output)

    def copy(self, source, destination):
        path = os.path.join(self.output_path, destination)
        head, tail = os.path.split(path)
        if not os.path.exists(head):
            os.makedirs(path)

        shutil.copy(source, path)
