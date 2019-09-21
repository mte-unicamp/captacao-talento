from django.db import models
# from django.core.mail import send_mail
# from trello_helper import Helper
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.utils import timezone
# import datetime as dt


class Hunter(models.Model):

    email = models.EmailField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    list_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name


class Seller(Hunter):
    """docstring for Seller"""

    # attributes

    # methods

    pass


class Contractor(Hunter):
    """docstring for Contractor"""

    # attributes

    # methods

    pass


class Company(models.Model):
    """docstring for Company"""

    # attributes

    # methods

    def __str__(self):
        return self.name


class Reminder(models.Model):
    """docstring for Reminder"""

    # attributes

    # methods

    pass
