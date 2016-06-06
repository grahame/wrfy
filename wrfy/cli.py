import argparse
import sys

from docker import Client
from fnmatch import fnmatch

from .image import Image
from .container import Container
from .volume import Volume
from .util import print_status_stream, make_registration_decorator, \
    log_action, log_any_error, log_issue, confirm_action
from .check import check_latest_image

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
    for container in Container.all(cli):
        log_action("killing container: %s" % (container))
        log_any_error(lambda: cli.kill(container.get('Id')))


@register_command
def rm_stopped(args):
    "remove all stopped containers"
    cli = Client()
    for container in sorted(Container.all(cli, {'status': 'exited'}), key=repr):
        log_action("removing stopped container: %s" % (container))
        log_any_error(lambda: cli.remove_container(container.get('Id')))


@register_command
def rmi_untagged(args):
    "remove all untagged images"
    cli = Client()
    for image in sorted(Image.all(cli, filters={'dangling': True}), key=repr):
        log_action("removing untagged image: %s" % (image))
        log_any_error(lambda: cli.remove_image(image.get('Id')))


@register_command
def rmi_matching(args):
    "remove images which have tags matching `pattern'"
    cli = Client()
    to_remove = []
    for image in sorted(Image.all(cli), key=repr):
        to_remove += [tag for tag in image.tags if fnmatch(tag, args.pattern)]
    if not to_remove:
        return
    background = ['Images with the following tags will be deleted:\n']
    for tag in to_remove:
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
    issues = []
    issues += check_latest_image(cli)
    for issue in issues:
        log_issue(issue)


def setup_rmi_matching(subparser):
    subparser.add_argument('pattern', help='glob pattern')
    subparser.add_argument('--force', help='don\'t ask to confirm', action='store_true')
rmi_matching.setup = setup_rmi_matching


@register_command
def rmv_dangling(args):
    "remove all dangling volumes"
    cli = Client()
    for volume in sorted(Volume.all(cli, filters={'dangling': True}), key=repr):
        log_action("removing dangling volume: %s" % (volume))
        cli.remove_volume(volume.get('Name'))


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
