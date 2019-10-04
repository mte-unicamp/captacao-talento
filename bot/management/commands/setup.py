from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):
        try:
            pass
        except Exception as e:
            raise CommandError('Setup failed')
