from .container import Container
from .image import Image
from .volume import Volume


def untagged_images_with_usage(cli):
    used_images = {}
    for container in Container.all(cli, all=True):
        used_images[container.get('Image')] = container
    for image in sorted(Image.all(cli, filters={'dangling': True}), key=repr):
        image_id = image.get('Id')
        yield image, used_images.get(image_id)


def dangling_volumes(cli):
    yield from sorted(Volume.all(cli, filters={'dangling': True}), key=repr)


def stopped_containers(cli):
    yield from (container for container in sorted(Container.all(cli, all=True), key=repr)
                if not container.get('State', {}).get('Running'))


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


def check_untagged_images(cli):
    issues = []
    for image, used_by in untagged_images_with_usage(cli):
        if used_by is None:
            issues.append('image %s: dangling' % (image))
    return issues


def check_dangling_volumes(cli):
    issues = []
    for volume in dangling_volumes(cli):
        issues.append('volumes %s: dangling' % (volume))
    return issues


def check_stopped_containers(cli):
    issues = []
    stopped_count = len(list(stopped_containers(cli)))
    if stopped_count > 0:
        issues.append('%d stopped containers - possibly unneeded' % (stopped_count))
    return issues
