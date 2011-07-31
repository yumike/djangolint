import ast

from .base import BaseAnalyzer, ModuleVisitor, Result


class ContextProcessorsVisitor(ast.NodeVisitor):

    def __init__(self):
        self.found = []

    deprecated_items = {
        'django.core.context_processors.auth':
            'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.PermWrapper':
            'django.contrib.auth.context_processors.PermWrapper',
        'django.core.context_processors.PermLookupDict':
            'django.contrib.auth.context_processors.PermLookupDict',
    }

    def visit_Str(self, node):
        if node.s in self.deprecated_items.keys():
            self.found.append((node.s, node))


class ContextProcessorsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = ContextProcessorsVisitor()
        visitor.visit(code)
        for name, node in visitor.found:
            propose = visitor.deprecated_items[name]
            result = Result(
                description = (
                    '%r function is deprecated, use %r instead' % (name, propose)
                ),
                path = filepath,
                line = node.lineno)
            lines = self.get_file_lines(filepath, node.lineno, node.lineno)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
                result.solution.add_line(lineno, text.replace(name, propose), important)
            yield result
