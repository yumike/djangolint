from .generic_views import GenericViewsAnalyzer
from .syntax_error import SyntaxErrorAnalyzer


registry = [
    GenericViewsAnalyzer,
    SyntaxErrorAnalyzer,
]
