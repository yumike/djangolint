from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Report


class Command(BaseCommand):

    help = 'Deletes expired reports'

    def handle(self, *args, **kwargs):
        Report.objects.delete_expired()
