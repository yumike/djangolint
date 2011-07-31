import ast
import os
from .context import Context


class BaseAnalyzer(object):
    """
    Base code analyzer class. Takes dict `file path => ast node` as first
    param and path to repository as second.

    Subclass this class and implement `analyze_file` method if you want to
    create new code analyzer.
    """

    surround_by = 2

    def __init__(self, code_dict, repo_path):
        self._file_lines = None
        self.code_dict = code_dict
        self.repo_path = repo_path

    def get_file_lines(self, filepath, lineno):
        """
        Yield code snippet from file `filepath` for line number `lineno`
        as tuples `(<line number>, <text>)` extending it by `surround_by`
        lines up and down if possible.
        """
        if self._file_lines is None:
            with open(os.path.join(self.repo_path, filepath)) as f:
                self._file_lines = f.readlines()
        start = max(0, lineno - self.surround_by - 1)
        stop = lineno + self.surround_by
        for i, line in enumerate(self._file_lines[start:stop], start=start):
            yield (i + 1, line.rstrip())

    def clear_file_lines_cache(self):
        self._file_lines = None

    def analyze_file(self, filepath, code):
        raise NotImplementedError

    def analyze(self):
        """
        Iterate over `code_dict` and yield all results from every file.
        """
        for filepath, code in self.code_dict.items():
            for result in self.analyze_file(filepath, code):
                yield result
            self.clear_file_lines_cache()


class CodeSnippet(list):
    """
    Represents code snippet as list of tuples `(<line number>, <importance>,
    <text>)`.

    Use `add_line` method to add new lines to the snippet.
    """

    def add_line(self, lineno, text, important=True):
        """
        Add new line to the end of snippet.
        """
        self.append((lineno, important, text))


class Result(object):
    """
    Represents the result of code analysis.
    """

    def __init__(self, description, path, line):
        self.description = description
        self.path = path
        self.line = line
        self.source = CodeSnippet()
        self.solution = CodeSnippet()


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
        """
        Get the name of the visited attribute.
        """
        return '.'.join(self.name)

    def visit_Attribute(self, node):
        self.generic_visit(node)
        self.name.append(node.attr)

    def visit_Name(self, node):
        self.name.append(node.id)

    def visit_Load(self, node):
        pass

    def generic_visit(self, node):
        # If attribute node consists not only from nodes of types `Attribute`
        # and `Name` mark it as unusable.
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
        """
        Update `names` context with interesting imported `aliases` using
        `get_path` function to get full path to the object by object name.
        """
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
        # Create new scope in `names` context if we are coming to function body
        self.names.push()
        self.generic_visit(node)
        self.names.pop()

    def visit_Assign(self, node):
        # Some assings attach interesting imports to new names.
        # Trying to parse it.
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
