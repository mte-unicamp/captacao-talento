from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
import os
import datetime as dt
# from trello_helper import Helper
# from django.core.validators import MinValueValidator, MaxValueValidator


class Hunter(models.Model):
    """
    * A hunter is any person in contact with a company;
    * Each has a unique list in a trello board;
    * We use their e-mail to send reminders if if has too long since
    the last answer from a company;
    * This class is inherited by Seller and Contractor (the two types
    of hunters)
    """

    email = models.EmailField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    list_id = models.CharField(max_length=100, null=True)

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


class Global(models.Model):
    """
    Set of global variabels used by other models
    """

    FINA = 'fina'
    CONS = 'cons'
    TECH = 'tech'
    COMM = 'comm'
    HEAL = 'heal'
    MANU = 'manu'
    RECR = 'recr'
    RESE = 'rese'

    CATEGORY_LIST = [FINA, CONS, TECH, COMM, HEAL, MANU, RECR, RESE]

    CATEGORY_CHOICES = (
        (FINA, 'Financial'), (CONS, 'Consulting'),
        (TECH, 'Technology'), (COMM, 'Communication'),
        (HEAL, 'Health'), (MANU, 'Manufacturing'),
        (RECR, 'Recruiting'), (RESE, 'Research'),
    )

    # seller stages
    FIRS = 'firs'
    NANS = 'nans'
    INTE = 'inte'
    REJE = 'reje'
    NEGO = 'nego'
    CLOS = 'clos'
    # fee type
    BRON = 'bron'
    SILV = 'silv'
    GOLD = 'gold'
    DIAM = 'diam'
    # contract type
    REGU = 'regu'
    STAR = 'star'
    OTHE = 'othe'
    CANC = 'canc'
    # payment form
    BOLE = 'bole'
    TRAN = 'tran'

    STAGE_SELLER_LIST = [FIRS, NANS, INTE, REJE, NEGO, CLOS]

    FEE_TYPE_LIST = [BRON, SILV, GOLD, DIAM, OTHE]

    CONTRACT_TYPE_LIST = [REGU, STAR, CANC]

    PAYMENT_FORM_LIST = [BOLE, TRAN]

    NO_REMINDER = [NANS, REJE, CLOS]

    STAGE_SELLER_CHOICES = (
        (FIRS, 'Initial Contact'), (NANS, 'No Answer'), (INTE, 'Interested'),
        (REJE, 'Rejected'), (NEGO, 'Negotiation'), (CLOS, 'Closed'),
    )

    FEE_TYPE_CHOICES = (
        (BRON, 'Bronze'), (SILV, 'Silver'), (GOLD, 'Gold'),
        (DIAM, 'Diamond'), (OTHE, 'Other'),
    )

    CONTRACT_TYPE_CHOICES = (
        (REGU, 'Regular'), (STAR, 'Startup'), (CANC, 'Cancelled'),
    )

    PAYMENT_FORM_CHOICES = (
        (BOLE, 'Boleto'), (TRAN, 'Transfer'),
    )

    # deadline variables
    ATTENTION_DEADLINE = models.IntegerField(default=8)
    URGENT_DEADLINE = models.IntegerField(default=15)

    SALES_LABEL_IDs = []
    POST_SALES_LABEL_IDs = []

class Company(models.Model):
    """docstring for Company"""

    name = models.CharField(max_length=100, unique=True)
    card_id = models.CharField(max_length=100, primary_key=True)
    seller = models.ForeignKey('Seller', on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=4, choices=Global.CATEGORY_CHOICES)
    seller_stage = models.CharField(
        max_length=4, choices=Global.STAGE_SELLER_CHOICES, default=Global.FIRS)
    last_activity = models.DateField(default=timezone.now)
    date_closed = models.DateField(default=dt.date.today)
    comments_number = models.IntegerField(default=0)
    main_contact = models.EmailField(blank=True)

    @property
    def inactive_time(self):
        return (timezone.now() - self.last_activity)

    @property
    def needs_reminder(self):
        return not (
            (self.inactive_time.days < Global.URGENT_DEADLINE) or (
                self.seller_stage in Global.NO_REMINDER)
        )

    @property
    def status_label(self):
        if self.inactive_time.days < Global.ATTENTION_DEADLINE:
            return 'updated'
        elif self.inactive_time.days < Global.URGENT_DEADLINE:
            return 'attention'
        else:
            return 'urgent'

    def set_last_activity(self):
        # TODO
        return

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class ClosedCompany(Company):

    company = models.OneToOneField('Company', on_delete=models.CASCADE)
    sec_card_id = models.CharField(max_length=100, primary_key=True)
    contractor = models.ForeignKey(
        'Contractor', on_delete=models.SET_NULL, null=True)
    fee_type = models.CharField(
        max_length=4, choices=Global.FEE_TYPE_CHOICES)
    contract_type = models.CharField(
        max_length=4, choices=Global.CONTRACT_TYPE_CHOICES)
    payment_form = models.CharField(
        max_length=4, choices=Global.PAYMENT_FORM_CHOICES)
    intake = models.IntegerField()
    needs_receipt = models.BooleanField()
    stand_size = models.IntegerField()
    stand_pos = models.CharField(max_length=10)
    custom_stand = models.BooleanField()
    payday = models.DateField()

    class Meta:
        verbose_name_plural = 'closedCompanies'


class Reminder(models.Model):
    """docstring for Reminder"""

    # attributes

    @classmethod
    def contact_reminder(seller):
        companies = []
        for c in seller.contact_list:
            if c.needs_reminder:
                companies.append(c)
        subject = "[Talento 2020] Lembrete de Captação"
        from_email = os.environ['EMAIL_HOST_USER']
        line_list = ["Olá, {seller}!",
                     "",
                     "Você precisa entrar em contato com a(s)\
                      empresa(s) a seguir:",
                     ]
        for c in companies:
            line_list.append("\t* {company} ({email});")
        line_list.append("Qualquer dúvida ou problema favor entrar \
            em contato pelo endereço {reply}")
        message = "\n".join(line_list).format(seller=seller.name,
                                              company=c.name,
                                              email=c.main_contact,
                                              reply=from_email)
        recipient_list = [seller.email]
        send_mail(subject, message, from_email, recipient_list)
