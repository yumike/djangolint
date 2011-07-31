import ast

from .base import (
    BaseAnalyzer, Result, AttributeVisitor, ModuleVisitor, set_lineno)


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
            return

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
