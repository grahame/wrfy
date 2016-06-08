import argparse
import sys
import re

from docker import Client
from fnmatch import fnmatch

from .image import Image
from .container import Container
from .util import print_status_stream, make_registration_decorator, \
    log_action, log_any_error, log_issue, log_issues, log_warnings, \
    confirm_action
from .check import check_latest_image, check_dangling_volumes, \
    check_untagged_images, untagged_images_with_usage, \
    check_stopped_containers, stopped_containers, \
    dangling_volumes

register_command, command_fns = make_registration_decorator()


@register_command
def pull_all(args):
    "pull all images"
    def status_title(tag, pad=None):
        title = 'pull %s' % (tag)
        if pad:
            title = '%*s' % (pad, title)
        return title

    cli = Client()
    tags = Image.repotags(cli)
    pad = max(len(status_title(t)) for t in tags)
    for tag in sorted(tags):
        log_action("pulling tag: %s" % (tag))
        print_status_stream(
            status_title(tag, pad),
            cli.pull(tag, stream=True))


@register_command
def kill_all(args):
    "kill all running containers"
    cli = Client()
    to_kill = list(sorted(Container.all(cli), key=repr))
    if not to_kill:
        return
    background = ['The following running containers will be killed:\n']
    background += [' • %s\n' % (container) for container in to_kill]
    if not args.force and not confirm_action(
            ''.join(background), 'Kill containers?'):
        return
    for container in to_kill:
        log_action("killing container: %s" % (container))
        log_any_error(lambda: cli.kill(container.get('Id')))


@register_command
def rm_stopped(args):
    "remove all containers which are not running"
    cli = Client()
    to_remove = list(stopped_containers(cli))
    if not to_remove:
        return
    background = ['The following stopped containers will be removed:\n']
    background += [' • %s\n' % (container) for container in to_remove]
    if not args.force and not confirm_action(
            ''.join(background), 'Remove containers?'):
        return
    for container in to_remove:
        log_action("removing container: %s" % (container))
        log_any_error(lambda: cli.remove_container(container.get('Id')))


@register_command
def rmv_dangling(args):
    "remove all dangling volumes"
    cli = Client()
    to_remove = list(dangling_volumes(cli))
    if not to_remove:
        return
    background = ['The following dangling volumes will be removed:\n']
    background += [' • %s\n' % (volume) for volume in to_remove]
    if not args.force and not confirm_action(
            ''.join(background), 'Remove volumes?'):
        return
    for volume in to_remove:
        log_action("removing dangling volume: %s" % (volume))
        cli.remove_volume(volume.name)


@register_command
def rmi_dangling(args):
    "remove all dangling (untagged) images"
    cli = Client()
    to_remove = []
    if not to_remove:
        return
    for image, used_by in untagged_images_with_usage(cli):
        if used_by:
            log_issue("not removing image: %s (in use by %s)" % (image, used_by))
        else:
            to_remove.append(image)
    background = ['The following dangling images will be removed:\n']
    background += [' • %s\n' % (image) for image in to_remove]
    if not args.force and not confirm_action(
            ''.join(background), 'Remove images?'):
        return
    for image in to_remove:
        log_action("removing dangling image: %s" % (image))
        log_any_error(lambda: cli.remove_image(image.get('Id')))


def setup_force(subparser):
    subparser.add_argument('--force', help='don\'t ask to confirm', action='store_true')

kill_all.setup = setup_force
rm_stopped.setup = setup_force
rmi_dangling.setup = setup_force
rmv_dangling.setup = setup_force


def match_iterator_glob_or_regexp(args, iterator, apply_fn):
    """
    returns the matching objects from `iterator`, using fnmatch
    unless args.e is set, in which case regular expression is used.
    `apply_fn` is applied to each object, returning a string to
    check match against.
    """
    if args.e:
        r = re.compile(args.pattern)

        def matcher(s):
            return r.match(s)
    else:
        def matcher(s):
            return fnmatch(s, args.pattern)

    for obj in iterator:
        match = apply_fn(obj)
        if matcher(match):
            yield obj


@register_command
def rm_matching(args):
    "remove containers whose name matches `pattern'"
    cli = Client()
    to_remove = list(
        match_iterator_glob_or_regexp(
            args,
            stopped_containers(cli),
            lambda c: c.name))
    if not to_remove:
        return
    background = ['The following containers will be deleted:\n']
    for container in sorted(to_remove, key=repr):
        background.append(' • %s\n' % (container))
    if not args.force and not confirm_action(
            ''.join(background), 'Delete matching containers?'):
        return
    for container in to_remove:
        log_action("removing container via tag: %s" % (container))
        log_any_error(lambda: cli.remove_container(container.get('Id')))


@register_command
def rmi_matching(args):
    "remove images which have tags matching `pattern'"
    cli = Client()

    def all_image_tags():
        for image in Image.all(cli):
            for tag in image.tags:
                yield tag
    to_remove = list(
        match_iterator_glob_or_regexp(
            args,
            all_image_tags(),
            lambda t: t))
    if not to_remove:
        return
    background = ['Images with the following tags will be deleted:\n']
    for tag in sorted(to_remove):
        background.append(' • %s\n' % (tag))
    if not args.force and not confirm_action(
            ''.join(background), 'Delete matching images?'):
        return
    for tag in to_remove:
        log_action("removing image via tag: %s" % (tag))
        log_any_error(lambda: cli.remove_image(tag))


@register_command
def doctor(args):
    "check for common issues"
    cli = Client()
    log_issues("containers running from old version of tag", "restart containers", check_latest_image(cli))
    log_issues("dangling volumes", "wrfy rmv-dangling", check_dangling_volumes(cli))
    log_issues("dangling dangling images", "wrfy rmi-dangling", check_untagged_images(cli))
    log_warnings("stopped containers", "wrfy rm-stoppped (... but check with docker ps -a first)", check_stopped_containers(cli))


def setup_globrm(subparser):
    subparser.add_argument('pattern', help='pattern (by default, glob)')
    subparser.add_argument('-e', help='treat pattern as regular expression', action='store_true')
    subparser.add_argument('--force', help='don\'t ask to confirm', action='store_true')
rm_matching.setup = setup_globrm
rmi_matching.setup = setup_globrm


def version():
    import pkg_resources
    version = pkg_resources.require("wrfy")[0].version
    print('''\
wrfy, version %s

Copyright © 2016 Grahame Bowland
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''' % (version))
    sys.exit(0)


def usage(parser):
    parser.print_usage()
    sys.exit(0)


def commands():
    for fn in command_fns:
        name = fn.__name__.replace('_', '-')
        yield name, fn, getattr(fn, 'setup', None), fn.__doc__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', action='store_true',
        help='print version and exit')

    subparsers = parser.add_subparsers(dest='name')
    for name, fn, setup_fn, help_text in sorted(commands()):
        subparser = subparsers.add_parser(name, help=help_text)
        subparser.set_defaults(func=fn)
        if setup_fn is not None:
            setup_fn(subparser)
    args = parser.parse_args()
    if args.version:
        version()
    if 'func' not in args:
        usage(parser)
    args.func(args)
