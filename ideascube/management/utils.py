from django.utils.termcolors import colorize


class Reporter:
    """Store reports and render them on demand."""

    ERROR = 1
    WARNING = 2
    NOTICE = 3
    LEVEL_LABEL = {
        ERROR: 'errors',
        WARNING: 'warnings',
        NOTICE: 'notices',
    }

    def __init__(self, verbosity):
        self.verbosity = verbosity
        self._reports = {
            self.ERROR: {},
            self.WARNING: {},
            self.NOTICE: {}
        }

    def compile(self):
        lines = []

        def write(text, **kwargs):
            lines.append(colorize(text=text, **kwargs))

        if self._reports:
            write('{space}Reports{space}'.format(space=' '*32), bg='blue',
                  fg='white')
            for level, reports in self._reports.items():
                if reports:
                    write(self.LEVEL_LABEL[level].title())
                for msg, data in reports.items():
                    write('- {} ({})'.format(msg, len(data)))
                    if self.verbosity >= level:
                        for item in data:
                            fg = 'red' if level == self.ERROR else 'white'
                            write('  . {}'.format(item), fg=fg)
        return lines

    def __str__(self):
        return '\n'.join(self.compile())

    def _report(self, level, msg, data):
        self._reports[level].setdefault(msg, [])
        self._reports[level][msg].append(data)

    def error(self, msg, data):
        self._report(self.ERROR, msg, data)

    def warning(self, msg, data):
        self._report(self.WARNING, msg, data)

    def notice(self, msg, data):
        self._report(self.NOTICE, msg, data)

    def has_errors(self):
        return bool(self._reports[self.ERROR])
