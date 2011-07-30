import os
from django.conf import settings


CONFIG = {
    'REPORT_EXPIRATION_DAYS': 30,
    'CLONES_ROOT': os.path.join(settings.PROJECT_ROOT, 'cloned_repos'),
}
CONFIG.update(getattr(settings, 'LINT_CONFIG', {}))
