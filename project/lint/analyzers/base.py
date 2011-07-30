import os


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
