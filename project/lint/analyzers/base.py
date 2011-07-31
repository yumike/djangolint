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

    def get_file_lines(self, filepath, start, stop):
        """
        Yield code snippet from file `filepath` for line number `lineno`
        as tuples `(<line number>, <importance>, <text>)` extending it by
        `surround_by` lines up and down if possible.

        If important part has blank lines at the bottom they will be removed.
        """

        if self._file_lines is None:
            with open(os.path.join(self.repo_path, filepath)) as f:
                self._file_lines = f.readlines()

        if stop is None:
            lines = self._file_lines[start - 1:]
        else:
            lines = self._file_lines[start - 1:stop]
        for i, line in enumerate(lines):
            lines[i] = [start + i, True, line.rstrip()]
        while lines and self.is_empty_line(lines[-1][-1]):
            lines.pop()

        if not lines:
            return []

        stop = lines[0][0]
        start = max(1, stop - self.surround_by)
        prefix_lines = []
        for i, line in enumerate(self._file_lines[start - 1:stop - 1], start=start):
            prefix_lines.append([i, False, line.rstrip()])

        start = lines[-1][0] + 1
        stop = start + self.surround_by
        suffix_lines = []
        for i, line in enumerate(self._file_lines[start - 1:stop - 1], start=start):
            suffix_lines.append([i, False, line.rstrip()])

        return prefix_lines + lines + suffix_lines

    def is_empty_line(self, line):
        return not line.split('#')[0].strip()

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


def set_lineno(meth):
    def decorator(self, node):
        self.push_lineno(node.lineno)
        result = meth(self, node)
        self.pop_lineno()
        return result
    decorator.__name__ = meth.__name__
    return decorator


class ModuleVisitor(ast.NodeVisitor):
    """
    Collect interesting imported names during module nodes visiting.
    """

    interesting = {}

    def __init__(self):
        self.names = Context()
        self.lineno = []
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
        self.lineno.append(lineno)
        lineno_level = self.get_lineno_level()
        for level in self.found.keys():
            if level < lineno_level:
                return
            for found in self.found[level]:
                if found[-1] is None and lineno >= found[-2]:
                    found[-1] = max(lineno - 1, found[-2])

    def pop_lineno(self):
        return self.lineno.pop()

    def get_lineno(self):
        return self.lineno[-1]

    def get_lineno_level(self):
        return len(self.lineno)

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

    @set_lineno
    def visit_Import(self, node):
        self.update_names(node.names, lambda x: x)

    @set_lineno
    def visit_ImportFrom(self, node):
        self.update_names(node.names, lambda x: '.'.join((node.module, x)))

    @set_lineno
    def visit_FunctionDef(self, node):
        # Create new scope in `names` context if we are coming to function body
        self.names.push()
        self.generic_visit(node)
        self.names.pop()

    @set_lineno
    def visit_Assign(self, node):
        # Some assingments attach interesting imports to new names.
        # Trying to parse it.
        visitor = AttributeVisitor()
        visitor.visit(node.value)
        if not visitor.is_usable:
            # Seems on the right side is not an attribute. Let's visit
            # assignment as it also can contain interesting code.
            self.generic_visit(node)
            return

        name = visitor.get_name()
        # skipping assignment if value is not interesting
        if name not in self.names:
            return

        # trying to parse the left-side attribute name
        for target in node.targets:
            visitor = AttributeVisitor()
            visitor.visit(target)
            if not visitor.is_usable:
                continue
            target = visitor.get_name()
            self.names[target] = self.names[name]

    @set_lineno
    def visit_Call(self, node):
        self.generic_visit(node)

    @set_lineno
    def visit_List(self, node):
        self.generic_visit(node)

    @set_lineno
    def visit_Tuple(self, node):
        self.generic_visit(node)


class DeprecatedCodeVisitor(ModuleVisitor):

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            name = visitor.get_name()
            if name in self.names:
                self.add_found(self.names[name], node)

    def visit_Name(self, node):
        if node.id in self.names:
            self.add_found(self.names[node.id], node)
