# Python std library
import datetime as dt
import os
import urllib.parse

# Django
from django.core.mail import send_mail
from django.db import models

# Project
from globalvars.models import Global


class Hunter(models.Model):
    """
    * A hunter is any person in contact with a company;
    * Each has a unique list in a trello board;
    * We use their e-mail to send reminders if if has too long since
    the last answer from a company;
    * This class is inherited by Seller and Contractor (the two types
    of hunters)
    """

    name = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField()
    list_id = models.CharField(max_length=100, null=True)

    @property
    def slug(self):
        return urllib.parse.quote(self.name.replace(" ", "-"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Seller(Hunter):
    """
    * A seller is someone that sells to the companies the opportunity
    to participate in the event;
    """

    @property
    def is_delayed(self):
        for c in Company.objects.filter(seller=self):
            if c.needs_reminder:
                return True
        return False

    @property
    def contact_count(self):
        return Company.objects.filter(seller=self).count()

    @property
    def contact_list(self):
        return list(Company.objects.filter(seller=self))

    @property
    def closed_count(self):
        return Company.objects.filter(seller=self, status=Global.CLOS).count()


class Contractor(Hunter):
    """
    * A contractor is someone that closes the contract with the companies;
    """

    @property
    def contact_count(self):
        return ClosedCompany.objects.filter(contractor=self).count()

    @property
    def contact_list(self):
        return list(ClosedCompany.objects.filter(contractor=self))


class PostSeller(Hunter):
    """
    """

    @property
    def contact_count(self):
        return ClosedCompany.objects.filter(postseller=self).count()

    @property
    def contact_list(self):
        return list(ClosedCompany.objects.filter(postseller=self))


class Company(models.Model):
    """docstring for Company"""

    name = models.CharField(max_length=100, unique=True)
    card_id = models.CharField(max_length=100, primary_key=True)
    seller = models.ForeignKey("Seller", on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=4, choices=Global.CATEGORY_CHOICES)
    seller_stage = models.CharField(
        max_length=4, choices=Global.STAGE_SELLER_CHOICES, default=Global.FIRS
    )
    last_activity = models.DateField(default=dt.date.today)
    comments_number = models.IntegerField(default=0)
    main_contact = models.EmailField(blank=True)
    closedcom = models.OneToOneField(
        "ClosedCompany", on_delete=models.SET_NULL, blank=True, null=True
    )

    @property
    def slug(self):
        return self.name.replace(" ", "-")

    @property
    def inactive_time(self):
        return dt.date.today() - self.last_activity

    @property
    def needs_reminder(self):
        g = Global.objects.all()[0]
        return not (
            (self.inactive_time.days < g.URGENT_DEADLINE)
            or (self.seller_stage in Global.NO_REMINDER)
        )

    @property
    def status_label(self):
        g = Global.objects.get(pk=1)
        if self.inactive_time.days < g.ATTENTION_DEADLINE:
            return Global.AUTO_LABEL_NAMES[0]
        elif self.inactive_time.days < g.URGENT_DEADLINE:
            return Global.AUTO_LABEL_NAMES[1]
        else:
            return Global.AUTO_LABEL_NAMES[2]

    def update(self):
        self.last_activity = dt.date.today()
        self.save()

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class ClosedCompany(models.Model):

    originalcom = models.OneToOneField("Company", on_delete=models.SET_NULL, null=True)
    sec_card_id = models.CharField(max_length=100, primary_key=True)
    contractor = models.ForeignKey("Contractor", on_delete=models.SET_NULL, null=True)
    postseller = models.ForeignKey("PostSeller", on_delete=models.SET_NULL, null=True)
    fee_type = models.CharField(max_length=4, choices=Global.FEE_TYPE_CHOICES)
    contract_type = models.CharField(max_length=4, choices=Global.CONTRACT_TYPE_CHOICES)
    payment_form = models.CharField(max_length=4, choices=Global.PAYMENT_FORM_CHOICES, blank=True)
    date_closed = models.DateField(default=dt.date.today)
    intake = models.IntegerField()
    needs_receipt = models.BooleanField(default=False)
    stand_size = models.IntegerField(blank=True, null=True)
    stand_pos = models.CharField(max_length=10, blank=True, null=True)
    custom_stand = models.BooleanField(default=False)
    payday = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "closedCompanies"

    def __str__(self):
        return f"Closed Object: {self.originalcom.name}"


class Reminder(models.Model):
    """docstring for Reminder"""

    from_email = os.environ["EMAIL_HOST_USER"]
    greeting = "Olá, {seller}!\n"
    signature = f"\nQualquer dúvida ou problema favor entrar em contato pelo endereço {from_email}"

    @staticmethod
    def new_company_reminder(company, hunter):
        pass

    @staticmethod
    def wrong_hunter_added(name):

        subject = "[Talento 2020] Uso incorreto da plataforma"
        message = f"{name} criou uma lista manualmente!"
        recipient_list = [os.environ["CONTACT"]]

        return send_mail(subject, message, Reminder.from_email, recipient_list)

    @staticmethod
    def wrong_company_added(company, seller):

        subject = "[Talento 2020] Uso incorreto da plataforma"
        body = f"Você tentou adicionar a empresa {company}, mas o fez da maneira errada! Por favor vá até a plataforma e clique em Adicionar Empresa para resolver esse problema."
        html_body = f"Você tentou adicionar a empresa <i>{company}</i>, mas o fez da maneira errada! Por favor vá até a plataforma e clique em <b><i>Adicionar Empresa</i></b> para resolver esse problema."
        message = "\n".join([Reminder.greeting, body, Reminder.signature]).format(
            seller=seller.name
        )
        html_message = (
            "<br>".join([Reminder.greeting, html_body, Reminder.signature])
            .format(seller=seller.name)
            .replace("\n", "<br>")
        )
        recipient_list = [seller.email]

        return send_mail(
            subject, message, Reminder.from_email, recipient_list, html_message=html_message
        )

    @staticmethod
    def wrong_company_closed(company):

        subject = "[Talento 2020] Uso incorreto da plataforma"
        body = f"Você tentou fechar a empresa {company.name}, mas o fez da maneira errada! Por favor vá até a plataforma e clique em Fechar Empresa para resolver esse problema."
        html_body = f"Você tentou fechar a empresa <i>{company.name}</i>, mas o fez da maneira errada! Por favor vá até a plataforma e clique em <b><i>Fechar Empresa</i></b> para resolver esse problema."
        message = "\n".join([Reminder.greeting, body, Reminder.signature]).format(
            seller=company.seller.name
        )
        html_message = (
            "<br>".join([Reminder.greeting, html_body, Reminder.signature])
            .format(seller=company.seller.name)
            .replace("\n", "<br>")
        )
        recipient_list = [company.seller.email]

        return send_mail(
            subject, message, Reminder.from_email, recipient_list, html_message=html_message
        )

    @staticmethod
    def contact_reminder(seller):

        subject = "[Talento 2020] Lembrete de Captação"
        body = "Você precisa entrar em contato com a(s) empresa(s) a seguir:"
        companies = [
            f"\t* {c.name} ({c.main_contact});" for c in seller.contact_list if c.needs_reminder
        ]
        message = "\n".join([Reminder.greeting, body, *companies, Reminder.signature]).format(
            seller=seller.name
        )
        recipient_list = [seller.email]

        return send_mail(subject, message, Reminder.from_email, recipient_list)
