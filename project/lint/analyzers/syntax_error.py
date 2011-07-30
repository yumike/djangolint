import os
from .base import BaseAnalyzer, Result


class SyntaxErrorAnalyzer(BaseAnalyzer):
    """
    Returns notes for all fiels with syntax error.
    """

    def analyze_file(self, path, code):
        if not isinstance(code, SyntaxError):
            return
        result = Result(description=code.msg, path=path, line=code.lineno)
        for i, line in self.get_file_lines(path, code.lineno):
            result.source.add_line(i, line, i == code.lineno)
        yield result
