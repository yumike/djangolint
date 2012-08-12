import ast

from .base import BaseAnalyzer, Result


class TemplateLoadersVisitor(ast.NodeVisitor):

    def __init__(self):
        self.found = []

    removed_items = {
        'django.template.loaders.app_directories.load_template_source':
            'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.load_template_source':
            'django.template.loaders.eggs.Loader',
        'django.template.loaders.filesystem.load_template_source':
            'django.template.loaders.filesystem.Loader',
    }

    def visit_Str(self, node):
        if node.s in self.removed_items.keys():
            self.found.append((node.s, node))


class TemplateLoadersAnalyzer(BaseAnalyzer):

    def analyze_file(self, filepath, code):
        if not isinstance(code, ast.AST):
            return
        visitor = TemplateLoadersVisitor()
        visitor.visit(code)
        for name, node in visitor.found:
            propose = visitor.removed_items[name]
            result = Result(
                description = (
                    '%r function has been deprecated in Django 1.2 and '
                    'removed in 1.4. Use %r class instead.' % (name, propose)
                ),
                path = filepath,
                line = node.lineno)
            lines = self.get_file_lines(filepath, node.lineno, node.lineno)
            for lineno, important, text in lines:
                result.source.add_line(lineno, text, important)
                result.solution.add_line(lineno, text.replace(name, propose), important)
            yield result
