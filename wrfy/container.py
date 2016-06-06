from .util import truncate_id


class Container:
    def __init__(self, cli, container_id):
        self.info = cli.inspect_container(container_id)

    def get(self, *args, **kwargs):
        return self.info.get(*args, **kwargs)

    @property
    def descr(self):
        return '%s[%s, %s]' % (self.info['Name'], self.info['Config']['Image'], truncate_id(self.info['Id']))

    def __repr__(self):
        return self.descr

    @classmethod
    def all(cls, cli, **kwargs):
        "construct an Image for all images"
        return [
            Container(cli, i['Id'])
            for i in cli.containers(**kwargs)]
