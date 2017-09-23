from __future__ import unicode_literals

from copy import deepcopy

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree


class SummaryTreeprocessor(Treeprocessor):
    @classmethod
    def itertree(cls, element, parent=()):
        for e in element:
            for p, e in cls.itertree(e, parent + (e,)):
                yield p, e

        # order is important, or removing the elements wouldnt work
        yield parent, element

    @classmethod
    def cleanup_marker(cls, marker, parents, element):
        element.text = element.text.replace(marker, '').strip()

        # remove the element if it only contained the marker
        if not element.text and len(element) == 0:
            parents[-2].remove(element)

    def run(self, root):
        found = False
        # instead of creating a new tree from scratch,
        # simply use the original one and remove elements
        clone = deepcopy(root)
        # lazy iteration wouldn't work, since we manipulate as we iterate
        for parents, element in list(self.itertree(clone, (clone,))):
            # if len(parents) is 1, only the root is left
            if found and len(parents) > 1:
                parents[-2].remove(element)
            elif element.text and self.config['marker'] in element.text:
                self.cleanup_marker(self.config['marker'], parents, element)
                found = True

        for parents, element in self.itertree(root, (root,)):
            if element.text and self.config['marker'] in element.text:
                self.cleanup_marker(self.config['marker'], parents, element)

        output = etree.tostring(clone, encoding='utf-8', method='html')
        for pp in self.markdown.postprocessors.values():
            output = pp.run(output)

        self.markdown.summary = output
        self.markdown.is_summarized = found


class SummaryExtension(Extension):
    TreeProcessorClass = SummaryTreeprocessor
    config = {
        'marker': [
            '[SUMMARY]',
            'summary goes until this mark is found, defaults to [SUMMARY]'
        ]
    }

    def __init__(self, configs=None):
        Extension.__init__(self)

        configs = dict() if configs is None else configs
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        summaryext = self.TreeProcessorClass(md)
        summaryext.config = self.getConfigs()
        md.treeprocessors.add("summarycext", summaryext, "_end")