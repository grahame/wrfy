from docker import Client
import argparse
import sys
from .ops import ImageInfo
from .util import print_status_stream


def command_pull_all(args):
    def status_title(tag, pad=None):
        title = 'pull %s' % (tag)
        if pad:
            title = '%*s' % (pad, title)
        return title

    cli = Client()
    info = ImageInfo(cli)
    pad = max(len(status_title(t)) for t in info.tags())
    for tag in sorted(info.tags()):
        print("updating tag %s" % (tag))
        print_status_stream(
            status_title(tag, pad),
            cli.pull(tag, stream=True))


def main():
    commands = {
        'pull': command_pull_all,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        help='action to take',
        nargs='?',
        default='pull',
        choices=commands.keys())
    parser.add_argument(
        '--version', action='store_true',
        help='print version and exit')
    args = parser.parse_args()
    if args.version:
        import pkg_resources
        version = pkg_resources.require("wrfy")[0].version
        print('''\
wrfy, version %s

Copyright © 2016 Grahame Bowland
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''' % (version))
        sys.exit(0)
    commands[args.command](args)
