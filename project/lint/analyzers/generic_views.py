import ast

from .base import BaseAnalyzer, Result, DeprecatedCodeVisitor


class GenericViewsVisitor(DeprecatedCodeVisitor):

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


class GenericViewsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = GenericViewsVisitor()
        visitor.visit(code)
        for name, node, start, stop in visitor.get_found():
            result = Result(
                description = (
                    '%r function has been deprecated in Django 1.3 and will '
                    'be removed in 1.5.' % name
                ),
                path = filepath,
                line = start)
            lines = self.get_file_lines(filepath, start, stop)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
            yield result
