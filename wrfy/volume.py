from .util import truncate_id


class Volume:
    unlabelled = '<unlabelled>'
    
    def __init__(self, cli, volume_id):
        self.info = cli.inspect_volume(volume_id)

    def get(self, *args, **kwargs):
        return self.info.get(*args, **kwargs)

    @property
    def descr(self):
        name = Volume.unlabelled
        labels = self.info['Labels']
        if labels:
            name = labels[0]
        return '%s[%s]' % (name, truncate_id(self.info['Name']))

    def __repr__(self):
        return self.descr

    @classmethod
    def all(cls, cli, **kwargs):
        "construct an Image for all images"
        response = cli.volumes(**kwargs)
        volumes = response['Volumes'] or []
        return [Volume(cli, i['Name']) for i in volumes]
