from django.core.management.base import BaseCommand, CommandError
from trello_helper.models import Updater
import os

class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):
        try:
            for c in Company.objects.all():
                Updater.set_last_activity(c)
                Updater.label_update(os.environ['SALES_BOARD_ID'])
        except Exception as e:
            raise CommandError('Update failed')
