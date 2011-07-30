"""Inspired by django.template.Context"""


class ContextPopException(Exception):
    """pop() has been called more times than push()"""


class Context(object):
    """A stack container for imports and assignments."""

    def __init__(self):
        self.dicts = [{}]

    def push(self):
        d = {}
        self.dicts.append(d)
        return d

    def pop(self):
        if len(self.dicts) == 1:
            raise ContextPopException
        return self.dicts.pop()

    def __setitem__(self, key, value):
        self.dicts[-1][key] = value

    def __getitem__(self, key):
        for d in reversed(self.dicts):
            if key in d:
                return d[key]
        raise KeyError

    def __delitem__(self, key):
        del self.dicts[-1][key]

    def has_key(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False

    def has_value(self, value):
        dict_ = {}
        for d in self.dicts:
            dict_.update(d)
        return value in dict_.values()

    def __contains__(self, key):
        return self.has_key(key)
