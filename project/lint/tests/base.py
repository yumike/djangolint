import os


TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))

EXAMPLE_PROJECT_FILES = [
    '__init__.py',
    'app/__init__.py',
    'app/admin.py',
    'app/forms.py',
    'app/models.py',
    'app/tests.py',
    'app/urls.py',
    'app/views.py',
    'bad_code.py',
    'good_code.py',
    'syntax_error.py',
]
