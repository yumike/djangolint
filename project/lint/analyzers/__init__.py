from .formtools import FormToolsAnalyzer
from .generic_views import GenericViewsAnalyzer
from .render_to_response import RenderToResponseAnalyzer
from .syntax_error import SyntaxErrorAnalyzer


registry = [
    FormToolsAnalyzer,
    GenericViewsAnalyzer,
    RenderToResponseAnalyzer,
    SyntaxErrorAnalyzer,
]
