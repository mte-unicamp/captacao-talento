from django.core.management.base import BaseCommand
from trello_helper.models import Updater
from bot.models import Company
import os


class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):

        try:
            Updater.label_update(os.environ['SALES_BOARD_ID'])
            m = 'LABELS UPDATED!'
            print(m)
        except Exception as e:
            m = 'LABEL UPATE FAILED! {0}: {1}'
            print(m.format(str(type(e))[8:-2], str(e)))

        for c in Company.objects.all():
            try:
                Updater.set_last_activity(c)
                m = 'UPDATED! {0}'.format(c.name)
                print(m)
            except Exception as e:
                m = 'FAILED! {0}-> {1}: {2}'
                print(m.format(c.name, str(type(e))[8:-2], str(e)))
                continue
