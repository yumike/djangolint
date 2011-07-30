from django.conf import settings


CONFIG = {
    'REPORT_EXPIRATION_DAYS': 30,
}
CONFIG.update(getattr(settings, 'LINT_CONFIG', {}))
