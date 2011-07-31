import ast
import re

from .base import BaseAnalyzer, Result, AttributeVisitor, ModuleVisitor
from .context import Context


class FormToolsVisitor(ModuleVisitor):

    interesting = {
        'django.contrib.formtools.utils': ['security_hash'],
        'django.contrib.formtools.utils.security_hash': None,
    }

    def __init__(self):
        ModuleVisitor.__init__(self)
        self.found = []

    def update_lineno(self, lineno):
        ModuleVisitor.update_lineno(self, lineno)
        if self.in_block and self.found and not self.found[-1][-1]:
            self.found[-1][-1] = self.lineno - 1

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            name = visitor.get_name()
            if name in self.names:
                self.found.append([name, node, self.lineno, None])

    def visit_Name(self, node):
        if node.id in self.names:
            self.found.append([node.id, node, self.lineno, None])


class FormToolsAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = FormToolsVisitor()
        visitor.visit(code)
        for name, node, start, stop in visitor.found:
            result = Result(
                description = '%r function is deprecated' % name,
                path = filepath,
                line = start)
            lines = self.get_file_lines(filepath, start, stop)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
            yield result
