import ast
import re

from .base import BaseAnalyzer, Result, DeprecatedCodeVisitor
from .context import Context


class FormToolsVisitor(DeprecatedCodeVisitor):

    interesting = {
        'django.contrib.formtools.utils': ['security_hash'],
        'django.contrib.formtools.utils.security_hash': None,
    }


class FormToolsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = FormToolsVisitor()
        visitor.visit(code)
        for name, node, start, stop in visitor.get_found():
            result = Result(
                description = '%r function is deprecated' % name,
                path = filepath,
                line = start)
            lines = self.get_file_lines(filepath, start, stop)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
            yield result
