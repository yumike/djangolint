import ast

from .base import BaseAnalyzer, Result, DeprecatedCodeVisitor


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
                description = (
                    "%r function has beed deprecated in Django 1.3 and "
                    "will be removed in 1.5. Use "
                    "'django.contrib.formtools.utils.form_hmac()' instead."
                    % name
                ),
                path = filepath,
                line = start)
            lines = self.get_file_lines(filepath, start, stop)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
            yield result
