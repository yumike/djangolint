import ast
import os


class Parser(object):

    def __init__(self, source):
        if not os.path.isabs(source):
            raise ValueError('Source path is not absolute: %s' % source)
        self.source = source

    def walk(self):
        for root, dirnames, filenames in os.walk(self.source):
            for filename in filenames:
                if filename.endswith('.py'):
                    yield os.path.join(root, filename)

    def relpath(self, path):
        return os.path.relpath(path, self.source)

    def parse_file(self, path):
        relpath = self.relpath(path)
        with open(path) as f:
            content = f.read()
        try:
            return (relpath, ast.parse(content, relpath))
        except SyntaxError, e:
            return (relpath, e)

    def parse(self):
        return dict(self.parse_file(path) for path in self.walk())
