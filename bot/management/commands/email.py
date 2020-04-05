from django.core.management.base import BaseCommand
from bot.models import Reminder, Seller
import time


class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):
        for s in Seller.objects.all():
            try:
                if s.is_delayed:
                    Reminder.contact_reminder(s)
                    time.sleep(5)
                    print(f'E-mail sent to {s.name}!')
                else:
                    print(f'{s.name} is up to date!')
            except Exception as e:
                m = 'FAILED! {0}-> {1}: {2}'
                print(m.format(s.name, str(type(e))[8:-2], str(e)))
                continue
