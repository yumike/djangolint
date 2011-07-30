import ast

from .base import BaseAnalyzer, Code, Result
from .context import Context


class AttributeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.is_usable = True
        self.name = []

    def get_name(self):
        return '.'.join(self.name)

    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.name.append(node.attr)

    def visit_Name(self, node):
        self.name.append(node.id)

    def visit_Load(self, node):
        pass

    def generic_visit(self, node):
        if not isinstance(node, ast.Attribute):
            self.is_usable = False
        ast.NodeVisitor.generic_visit(self, node)


class ModuleVisitor(ast.NodeVisitor):

    def __init__(self, interesting):
        self.interesting = interesting
        self.names = Context()
        self.found = []

    def update_names(self, aliases, get_path):
        for alias in aliases:
            path = get_path(alias.name)
            if path not in self.interesting:
                continue
            if self.interesting[path]:
                for attr in self.interesting[path]:
                    name = '.'.join((alias.asname or alias.name, attr))
                    self.names[name] = '.'.join((path, attr))
            else:
                name = alias.asname or alias.name
                self.names[name] = path

    def visit_Import(self, node):
        self.update_names(node.names, lambda x: x)

    def visit_ImportFrom(self, node):
        self.update_names(node.names, lambda x: '.'.join((node.module, x)))

    def visit_FunctionDef(self, node):
        self.names.push()
        self.generic_visit(node)
        self.names.pop()

    def visit_Assign(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node.value)
        if not visitor.is_usable:
            return
        name = visitor.get_name()
        if name not in self.names:
            return
        for target in node.targets:
            visitor = AttributeVisitor()
            visitor.visit(target)
            if not visitor.is_usable:
                continue
            target = visitor.get_name()
            self.names[target] = self.names[name]

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            name = visitor.get_name()
            if name in self.names:
                self.found.append((name, node))

    def visit_Name(self, node):
        if node.id in self.names:
            self.found.append((node.id, node))


class GenericViewsAnalyzer(BaseAnalyzer):

    deprecated = {
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

    def analyze_file(self, path, code):
        if not isinstance(code, ast.AST):
            return
        visitor = ModuleVisitor(self.deprecated)
        visitor.visit(code)
        for name, node in visitor.found:
            result = Result('%r is deprecated' % name, path, node.lineno)
            for i, line in self.get_file_lines(path, node.lineno):
                result.source.add_line(i, line, i == node.lineno)
            yield result
