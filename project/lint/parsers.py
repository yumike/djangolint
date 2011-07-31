import ast
import os


class Parser(object):
    """
    Find all *.py files inside `repo_path` and parse its into ast nodes.

    If file has syntax errors SyntaxError object will be returned except
    ast node.
    """

    def __init__(self, repo_path):
        if not os.path.isabs(repo_path):
            raise ValueError('Repository path is not absolute: %s' % repo_path)
        self.repo_path = repo_path

    def walk(self):
        """
        Yield absolute paths to all *.py files inside `repo_path` directory.
        """
        for root, dirnames, filenames in os.walk(self.repo_path):
            for filename in filenames:
                if filename.endswith('.py'):
                    yield os.path.join(root, filename)

    def relpath(self, path):
        return os.path.relpath(path, self.repo_path)

    def parse_file(self, path):
        relpath = self.relpath(path)
        with open(path) as f:
            content = f.read()
        try:
            return (relpath, ast.parse(content, relpath))
        except SyntaxError, e:
            return (relpath, e)

    def parse(self):
        return dict(self.parse_file(filepath) for filepath in self.walk())
