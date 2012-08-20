from django.utils.encoding import force_unicode, smart_str
from docutils.core import publish_parts


def rst2html(text):
    parts = publish_parts(source=smart_str(text), writer_name='html4css1')
    return force_unicode(parts['fragment'])
