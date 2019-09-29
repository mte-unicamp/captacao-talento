from django.db import models
from django.utils import timezone
# from django.core.mail import send_mail
# from trello_helper import Helper
# from django.core.validators import MinValueValidator, MaxValueValidator
# import datetime as dt


class Hunter(models.Model):
    """
    * A hunter is any person in contact with a company;
    * Each has a unique list in a trello board;
    * We use their e-mail to send reminders if if has too long since
    the last answer from a company;
    * This class is inherited by Seller and Contractor (the two types
    of hunters)
    """

    email = models.EmailField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
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
    def closed_count(self):
        return Company.objects.filter(seller=self, status=Global.CLOS).count()


class Contractor(Hunter):
    """
    * A contractor is someone that closes the contract with the companies;
    """

    @property
    def contact_count(self):
        return Company.objects.filter(contractor=self).count()


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
    # contractor stages
    BRON = 'bron'
    SILV = 'silv'
    GOLD = 'gold'
    DIAM = 'diam'
    STAR = 'star'
    OTHE = 'othe'
    CANC = 'canc'

    STAGE_SELLER_LIST = [FIRS, NANS, INTE, REJE, NEGO, CLOS]

    STAGE_CONTRACTOR_LIST = [BRON, SILV, GOLD, DIAM, STAR, OTHE, CANC]

    NO_REMINDER = [NANS, REJE, CLOS]

    STAGE_SELLER_CHOICES = (
        (FIRS, 'Initial Contact'), (NANS, 'No Answer'),
        (INTE, 'Interested'), (REJE, 'Rejected'),
        (NEGO, 'Negotiation'), (CLOS, 'Closed'),
    )

    STAGE_CONTRACTOR_CHOICES = (
        (BRON, 'Bronze'), (SILV, 'Silver'),
        (GOLD, 'Gold'), (DIAM, 'Diamond'),
        (STAR, 'Startup'), (OTHE, 'Other'),
        (CANC, 'Cancelled'),
    )

    # deadline variables
    ATTENTION_DEADLINE = models.IntegerField(default=8)
    URGENT_DEADLINE = models.IntegerField(default=15)


class Company(models.Model):
    """docstring for Company"""

    name = models.CharField(max_length=100)
    card_id = models.CharField(max_length=100, primary_key=True)
    seller = models.ForeignKey('Seller', on_delete=models.SET_NULL, null=True)
    contractor = models.ForeignKey(
        'Contractor', on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=4, choices=Global.CATEGORY_CHOICES)
    seller_stage = models.CharField(
        max_length=4, choices=Global.STAGE_SELLER_CHOICES, default=Global.FIRS)
    contractor_stage = models.CharField(
        max_length=4, choices=Global.STAGE_CONTRACTOR_CHOICES, blank=True)
    last_activity = models.DateTimeField(default=timezone.now)
    date_closed = models.DateTimeField()
    comments_number = models.IntegerField(default=0)

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


class Reminder(models.Model):
    """docstring for Reminder"""

    # attributes

    # methods

    pass
