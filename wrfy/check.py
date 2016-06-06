from .container import Container
from .image import Image


def check_latest_image(cli):
    issues = []
    for container in Container.all(cli):
        # determine the tag this container was launched from
        launched_tag = container.get('Config', {}).get('Image')
        if launched_tag is None:
            continue
        current_image = Image(cli, launched_tag)
        running_image_id = container.get('Image')
        current_image_id = current_image.get('Id')
        if running_image_id != current_image_id:
            issues.append('running container %s: launched from outdated version of tag' % (container))
    return issues
