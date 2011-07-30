import ast
import os
from .context import Context


class BaseAnalyzer(object):

    surround_by = 2

    def __init__(self, code, source):
        self.code = code
        self.source = source

    def get_file_lines(self, path, lineno):
        if not hasattr(self, '_file_lines'):
            with open(os.path.join(self.source, path)) as f:
                self._file_lines = f.readlines()
        start = max(0, lineno - self.surround_by - 1)
        stop = lineno + self.surround_by
        for i, line in enumerate(self._file_lines[start:stop], start=start):
            yield (i + 1, line.rstrip())

    def analyze_file(self, path, code):
        raise NotImplementedError

    def analyze(self):
        for path, code in self.code.items():
            for result in self.analyze_file(path, code):
                yield result


class Code(list):

    def add_line(self, line, text, important=True):
        self.append((line, important, text))


class Result(object):

    def __init__(self, description, path, line):
        self.description = description
        self.path = path
        self.line = line
        self.source = Code()
        self.solution = Code()


class AttributeVisitor(ast.NodeVisitor):
    """
    Process attribute node and build the name of the attribute if possible.

    Currently only simple expressions are supported (like `foo.bar.baz`).
    If it is not possible to get attribute name as string `is_usable` is
    set to `True`.

    After `visit()` method call `get_name()` method can be used to get
    attribute name if `is_usable` == `True`.
    """

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
        """
        If attribute node consists not only from nodes of types `Attribute`
        and `Name` mark it as unusable.
        """
        if not isinstance(node, ast.Attribute):
            self.is_usable = False
        ast.NodeVisitor.generic_visit(self, node)


class ModuleVisitor(ast.NodeVisitor):
    """
    Collect interesting imported names during module nodes visiting.
    """

    interesting = {}

    def __init__(self):
        self.names = Context()

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
