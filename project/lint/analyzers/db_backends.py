import ast

from .base import BaseAnalyzer, Result


DESCRIPTION = """
``{name}`` database backend has been deprecated in Django 1.2 and removed in 1.4.
Use ``{propose}`` instead.
"""


class DB_BackendsVisitor(ast.NodeVisitor):

    def __init__(self):
        self.found = []

    removed_items = {
        'django.db.backends.postgresql':
            'django.db.backends.postgresql_psycopg2',

    }

    def visit_Str(self, node):
        if node.s in self.removed_items.keys():
            self.found.append((node.s, node))


class DB_BackendsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = DB_BackendsVisitor()
        visitor.visit(code)
        for name, node in visitor.found:
            propose = visitor.removed_items[name]
            result = Result(
                description = DESCRIPTION.format(name=name, propose=propose),
                path = filepath,
                line = node.lineno)
            lines = self.get_file_lines(filepath, node.lineno, node.lineno)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
                result.solution.add_line(lineno, text.replace(name, propose), important)
            yield result
