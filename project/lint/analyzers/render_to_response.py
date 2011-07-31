import ast

from .base import (
    BaseAnalyzer, Result, AttributeVisitor, ModuleVisitor, set_lineno)
from .context import Context


class CallVisitor(ast.NodeVisitor):
    """
    Collects all usable attributes and names inside function call.
    """

    def __init__(self):
        self.names = set()

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            self.names.add(visitor.get_name())

    def visit_Name(self, node):
        self.names.add(node.id)


class RenderToResponseVisitor(ModuleVisitor):

    interesting = {
        'django.shortcuts': ['render_to_response'],
        'django.shortcuts.render_to_response': None,
        'django.template': ['RequestContext'],
        'django.template.RequestContext': None,
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

    @set_lineno
    def visit_Call(self, node):
        # Check if calling attribute is usable...
        visitor = AttributeVisitor()
        visitor.visit(node.func)
        if not visitor.is_usable:
            return

        # ...and if interesting
        name = visitor.get_name()
        if name not in self.names:
            return

        # ... and also if it is actually `render_to_response` call.
        if self.names[name] != 'django.shortcuts.render_to_response':
            pass

        # Check if it contains `RequestContext`. If so, add to `found`.
        visitor = CallVisitor()
        visitor.visit(node)
        for subname in visitor.names:
            if subname not in self.names:
                continue
            if self.names[subname] == 'django.template.RequestContext':
                self.add_found(name, node)


class RenderToResponseAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = RenderToResponseVisitor()
        visitor.visit(code)
        for name, node, start, stop in visitor.get_found():
            result = Result(
                description = (
                    "this %r usage case can be replaced with 'render' "
                    "function from 'django.shortcuts' package." % name),
                path = filepath,
                line = start)
            lines = self.get_file_lines(filepath, start, stop)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
            yield result
