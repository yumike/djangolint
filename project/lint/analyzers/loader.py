from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.functional import memoize


_analyzers_cache = {}


def clear_analyzers_cache():
    global _analyzers_cache
    _analyzers_cache.clear()


def load_analyzer(analyzer_name):
    module_name, attr = analyzer_name.rsplit('.', 1)
    try:
        module = import_module(module_name)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error importing analyzer %s: "%s"' % (analyzer_name, e))
    try:
        analyzer = getattr(module, attr)
    except AttributeError, e:
        raise ImproperlyConfigured(
            'Error importing analyzer %s: "%s"' % (analyzer_name, e))
    return analyzer


def get_analyzers():
    analyzers = []
    for analyzer_name in getattr(settings, 'LINT_ANALYZERS', ()):
        analyzers.append(load_analyzer(analyzer_name))
    return analyzers
get_analyzers = memoize(get_analyzers, _analyzers_cache, 0)
