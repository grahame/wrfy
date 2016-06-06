import progressbar
import json
from progressbar import FormatLabel, Percentage, Bar, RotatingMarker


def print_status_stream(title, stream):
    widgets = [title, FormatLabel(''), ' ', Percentage(), ' ', Bar(), ' ', RotatingMarker()]
    bar = progressbar.ProgressBar(widgets=widgets, max_value=255)

    def print_error(status):
        print(status['error'])

    def print_status(status):
        progress = status.get('progressDetail')
        if progress:
            widgets[1] = FormatLabel("%12s" % (status['status']))
            prog = int(round(255 * ((progress['current'] / progress['total']))))
            bar.update(prog)

    def print_unknown(status):
        print(status)

    for line in stream:
        status = json.loads(line.decode('utf8'))
        if 'error' in status:
            print_error(status)
        elif 'status' in status:
            print_status(status)
        else:
            print_unknown(status)
