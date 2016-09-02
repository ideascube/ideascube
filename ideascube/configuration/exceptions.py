class InvalidConfigurationValueError(Exception):
    def __str__(self):
        return (
            'Invalid type for configuration key "%s.%s": expected %s, got '
            '%s' % self.args)


class NoSuchConfigurationKeyError(Exception):
    def __str__(self):
        return 'Unknown configuration key: "%s.%s"' % self.args


class NoSuchConfigurationNamespaceError(Exception):
    def __str__(self):
        return 'Unknown configuration namespace: "%s"' % self.args
