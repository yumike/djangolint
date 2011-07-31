import ast

from .base import BaseAnalyzer, Result, AttributeVisitor, ModuleVisitor
from .context import Context


class GenericViewsVisitor(ModuleVisitor):

    interesting = {
        'django.views.generic.simple': ['direct_to_template', 'redirect_to'],
        'django.views.generic.simple.direct_to_template': None,
        'django.views.generic.simple.redirect_to': None,

        'django.views.generic.date_based': [
            'archive_index', 'archive_year', 'archive_month', 'archive_week',
            'archive_day', 'archive_today', 'archive_detail'],
        'django.views.generic.date_based.archive_index': None,
        'django.views.generic.date_based.archive_year': None,
        'django.views.generic.date_based.archive_month': None,
        'django.views.generic.date_based.archive_week': None,
        'django.views.generic.date_based.archive_day': None,
        'django.views.generic.date_based.archive_today': None,
        'django.views.generic.date_based.archive_detail': None,

        'django.views.generic.list_detail': ['object_list', 'object_detail'],
        'django.views.generic.list_detail.object_list': None,
        'django.views.generic.list_detail.object_detail': None,

        'django.views.generic.create_update': [
            'create_object', 'update_object', 'delete_object'],
        'django.views.generic.create_update.create_object': None,
        'django.views.generic.create_update.update_object': None,
        'django.views.generic.create_update.delete_object': None,
    }

    def __init__(self):
        ModuleVisitor.__init__(self)
        self.found = []

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            name = visitor.get_name()
            if name in self.names:
                self.found.append((name, node))

    def visit_Name(self, node):
        if node.id in self.names:
            self.found.append((node.id, node))


class GenericViewsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = GenericViewsVisitor()
        visitor.visit(code)
        for name, node in visitor.found:
            result = Result(
                description = '%r function is deprecated' % name,
                path = filepath,
                line = node.lineno)
            for lineno, text in self.get_file_lines(filepath, node.lineno):
                result.source.add_line(lineno, text, lineno == node.lineno)
            yield result
