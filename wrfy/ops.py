
class ImageInfo:
    def __init__(self, cli):
        self.update(cli)

    def update(self, cli):
        self.images = cli.images()

    def tags(self):
        "returns all tags applied to images in the docker instance"
        tags = set()
        for image in self.images:
            for tag in image['RepoTags']:
                if tag == '<none>:<none>':
                    continue
                tags.add(tag)
        return tags
