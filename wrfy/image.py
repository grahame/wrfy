from .util import truncate_id


class Image:
    untagged = '<none>:<none>'

    def __init__(self, cli, image_id):
        self.info = cli.inspect_image(image_id)

    def get(self, *args, **kwargs):
        return self.info.get(*args, **kwargs)

    @property
    def tags(self):
        return self.info['RepoTags']

    @property
    def descr(self):
        name = Image.untagged
        if self.tags:
            name = self.tags[0]
        return '%s[%s]' % (name, truncate_id(self.info['Id']))

    def __repr__(self):
        return self.descr

    @classmethod
    def all(cls, cli, **kwargs):
        "construct an Image for all images"
        return [Image(cli, i['Id']) for i in cli.images(**kwargs)]

    @classmethod
    def repotags(cls, cli):
        "returns the set of all repo tags"
        tags = set()
        images = Image.all(cli)
        for image in images:
            for tag in image.info['RepoTags']:
                if tag == Image.untagged:
                    continue
                tags.add(tag)
        return tags
