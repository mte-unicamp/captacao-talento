import os
import time

from django.core.management.base import BaseCommand

from bot.models import Company, Contractor, Reminder, Seller
from globalvars.models import Global
from trello_helper.models import Helper


class Command(BaseCommand):
    help = "help"

    def handle(self, *args, **options):
        for s in Seller.objects.all():
            try:
                if s.is_delayed:
                    Reminder.contact_reminder(s)
                    time.sleep(5)
                    print(f"E-mail sent to {s.name} because they are delayed!")
                else:
                    print(f"{s.name} is up to date!")
            except Exception as e:
                m = "FAILED! {0}-> {1}: {2}"
                print(m.format(s.name, str(type(e))[8:-2], str(e)))
                continue

        reverse_manual_label_names = {k: v for v, k in Global.MANUAL_LABEL_NAMES.items()}
        for label in Helper.get_nested_objs(
            "boards", os.environ["SALES_BOARD_ID"], "labels"
        ).json():
            if label["name"] == reverse_manual_label_names[Global.CLOS]:
                closed_label = label

        for c in Company.objects.all():
            time.sleep(1)
            if (
                closed_label in Helper.get_nested_objs("cards", c.card_id, "labels").json()
                and not c.closedcom
            ):
                try:
                    Reminder.wrong_company_closed(c)
                    time.sleep(5)
                    print(f"E-mail sent to {c.seller.name} because closed company wrongly!")
                except Exception as e:
                    m = "FAILED! {0}-> {1}: {2}"
                    print(m.format(s.name, str(type(e))[8:-2], str(e)))
                    continue

        for l in Helper.get_nested_objs("boards", os.environ["SALES_BOARD_ID"], "lists").json():
            try:
                s = Seller.objects.get(name=l["name"])
                for c in Helper.get_nested_objs("lists", l["id"], "cards").json():
                    try:
                        Company.objects.get(card_id=c["id"])
                    except Company.DoesNotExist:
                        try:
                            Reminder.wrong_company_added(c["name"], s)
                            time.sleep(5)
                            print(f'{c["name"]} not in database! E-mail sent!')
                        except Exception as e:
                            m = "FAILED! {0}-> {1}: {2}"
                            print(m.format(s.name, str(type(e))[8:-2], str(e)))
                            continue
            except Seller.DoesNotExist:
                try:
                    Reminder.wrong_hunter_added(l["name"])
                    time.sleep(5)
                    print(f'E-mail sent because {l["name"]} added hunter wrongly!')
                except Exception as e:
                    m = "FAILED! {0}-> {1}: {2}"
                    print(m.format(s.name, str(type(e))[8:-2], str(e)))
                    continue

        for l in Helper.get_nested_objs("boards", os.environ["CONTRACTS_BOARD_ID"], "lists").json():
            try:
                Contractor.objects.get(name=l["name"])
            except Contractor.DoesNotExist:
                try:
                    Reminder.wrong_hunter_added(l["name"])
                    time.sleep(5)
                    print(f'E-mail sent because {l["name"]} added hunter wrongly!')
                except Exception as e:
                    m = "FAILED! {0}-> {1}: {2}"
                    print(m.format(s.name, str(type(e))[8:-2], str(e)))
                    continue
