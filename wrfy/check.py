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
    for volume in sorted(Volume.all(cli, filters={'dangling': True}), key=repr):
        issues.append('volumes %s: dangling' % (volume))
    return []
