from __future__ import unicode_literals

import os


class Writer(object):
    def __init__(self, output_path, **kwargs):
        self.output_path = output_path
        self.kwargs = kwargs

    def write(self, template, context, path):
        lcontext = self.kwargs.copy()
        lcontext.update(context.copy())

        output = template.render(**lcontext)

        path = os.path.join(self.output_path, path)
        head, tail = os.path.split(path)
        if not os.path.exists(head):
            os.makedirs(head)

        with open(path, 'w') as f:
            f.write(output)
