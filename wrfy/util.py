import progressbar
import json
from progressbar import FormatLabel, Percentage, Bar, RotatingMarker


def log_action(s):
    print("➡  %s" % (s))


def log_issue(s):
    print("🔥 %s" % (s))


def log_warning(s):
    print("⚠️  %s" % (s))


def log_warnings(header, fix, issues):
    if not issues:
        return
    print(header)
    for issue in issues:
        log_warning(issue)
    if fix:
        print("fix (if desired): %s" % (fix))


def log_issues(header, fix, issues):
    if not issues:
        return
    print(header)
    if fix:
        print("💊 %s" % (fix))
    for issue in issues:
        log_issue(issue)


def log_any_error(fn):
    try:
        fn()
    except Exception as e:
        print("😞  %s" % (str(e)))


def confirm_action(background, question):
    print(background)
    return input('🤔  %s [yes/no]: ' % (question)) == 'yes'


def truncate_id(s):
    return s.split(':', 1)[-1][:12]


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


def make_registration_decorator():
    """
    returns a (decorator, list). any function decorated with
    the returned decorator will be appended to the list
    """
    registered = []

    def _register(fn):
        registered.append(fn)
        return fn

    return _register, registered
