import os
from .base import BaseAnalyzer, Result


class SyntaxErrorAnalyzer(BaseAnalyzer):
    """
    Return notes for all fiels with syntax error.
    """

    def analyze_file(self, path, code):
        if not isinstance(code, SyntaxError):
            return
        result = Result(description=code.msg, path=path, line=code.lineno)
        lines = self.get_file_lines(path, code.lineno, code.lineno)
        for i, important, line in lines:
            result.source.add_line(i, line, important)
        yield result
