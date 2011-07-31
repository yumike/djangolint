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
        self.found = {}

    def add_found(self, name, node):
        lineno_level = self.get_lineno_level()
        if lineno_level not in self.found:
            self.found[lineno_level] = []
        self.found[lineno_level].append([name, node, self.get_lineno(), None])

    def get_found(self):
        for level in self.found.values():
            for found in level:
                yield found

    def push_lineno(self, lineno):
        ModuleVisitor.push_lineno(self, lineno)
        lineno_level = self.get_lineno_level()
        for level in self.found.keys():
            if level < lineno_level:
                return
            for found in self.found[level]:
                if found[-1] is None:
                    found[-1] = max(lineno - 1, found[-2])

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            name = visitor.get_name()
            if name in self.names:
                self.add_found(name, node)

    def visit_Name(self, node):
        if node.id in self.names:
            self.add_found(node.id, node)


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
