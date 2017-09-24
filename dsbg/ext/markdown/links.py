from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from urlparse import urljoin


class RelativeImageLinkTreeprocessor(Treeprocessor):
    def __init__(self, url_prefix_resolver, markdown_instance=None):
        Treeprocessor.__init__(self, markdown_instance=markdown_instance)

        self.url_prefix_resolver = url_prefix_resolver

    def run(self, root):
        url_prefix = self.url_prefix_resolver().rstrip('/') + '/'

        for image in root.iter('img'):
            url = image.attrib['src']
            image.set('src', urljoin(url_prefix, url))


class RelativeImageLinkExtension(Extension):
    TreeProcessorClass = RelativeImageLinkTreeprocessor

    def __init__(self, url_prefix_resolver, configs=None):
        Extension.__init__(self)

        self.url_prefix_resolver = url_prefix_resolver

        configs = dict() if configs is None else configs
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        extension = self.TreeProcessorClass(self.url_prefix_resolver, md)
        extension.config = self.getConfigs()
        md.treeprocessors['relativeimagelink'] = extension
