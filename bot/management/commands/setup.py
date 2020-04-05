from django.core.management.base import BaseCommand, CommandError
from globalvars.models import Global


class Command(BaseCommand):
    help = 'help'

    def handle(self, *args, **options):
        try:
            if not Global.objects.all():
                Global().save()
        except Exception as e:
            m = 'Setup failed! {0}: {1}'
            raise CommandError(m.format(str(type(e))[8:-2], str(e)))
