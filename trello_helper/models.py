from django.db import models
import os
import requests as re
import time
from globalvars.models import Global
from bot.models import (
    Seller, Contractor, PostSeller,
    Reminder, Company,
)


class Helper(models.Model):
    """docstring for Helper"""

    api_url = "https://api.trello.com/1"

    @staticmethod
    def generic_request(ext_obj, obj_id, nested_obj):
        url = '{}/{}/{}/{}'.format(Helper.api_url, ext_obj,
                                   obj_id, nested_obj)
        querystring = {
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        time.sleep(.05)  # this avoids making too many requests
        return url, querystring

    @staticmethod
    def get_nested_objs(ext_obj, obj_id, nested_obj=''):
        url, querystring = Helper.generic_request(ext_obj, obj_id, nested_obj)
        return re.get(url, params=querystring)

    @staticmethod
    def post_card(name, list_id):
        url = f'{Helper.api_url}/cards'
        querystring = {
            'name': name,
            'idList': list_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return re.post(url, params=querystring)

    @staticmethod
    def post_list(name, board_id):
        url = f'{Helper.api_url}/lists'
        querystring = {
            'name': name,
            'idBoard': board_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return re.post(url, params=querystring)

    @staticmethod
    def put_card_in_list(card_id, list_id):
        url = f'{Helper.api_url}/cards/{card_id}'
        querystring = {
            'idList': list_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return re.post(url, params=querystring)

    @staticmethod
    def post_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        querystring.update({'value': label_id})
        return re.post(url, params=querystring)

    @staticmethod
    def delete_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        url = '{}/{}'.format(url, label_id)
        return re.delete(url, params=querystring)


class Updater(models.Model):
    """docstring for Updater"""

    @staticmethod
    def set_last_activity(company):
        card = Helper.get_nested_objs('cards', company.card_id).json()
        labels = card['labels']
        labels_names = [i['name'] for i in labels]
        for stage in reversed(Global.MANUAL_LABEL_NAMES):
            if stage in labels_names and company.seller_stage != Global.MANUAL_LABEL_NAMES[stage]:
                company.update()
                company.seller_stage = Global.MANUAL_LABEL_NAMES[stage]
                company.save()
                break
        if card['badges']['comments'] > company.comments_number:
            company.update()
            company.comments_number = card['badges']['comments']
            company.save()

    @staticmethod
    def assign_new_hunter(company, hunter):
        if type(hunter) == Seller:
            company.seller = hunter
        elif type(hunter) == Contractor:
            company.closedcom.contractor = hunter
        elif type(hunter) == PostSeller:
            company.closedcom.postseller = hunter
        else:
            raise TypeError('Hunter must be Seller, Contractor or PostSeller')
        company.update()
        company.save()
        if type(hunter) != PostSeller:
            Helper.put_card_in_list(company.card_id, hunter.list_id)
        Reminder.new_company_reminder(company, hunter)

    @staticmethod
    def label_update(board_id):

        cards = Helper.get_nested_objs('boards', board_id, 'cards').json()
        labels = Helper.get_nested_objs('boards', board_id, 'labels').json()

        for l in labels:
            if l['name'] == Global.AUTO_LABEL_NAMES[0]:
                upd_id = l['id']
            elif l['name'] == Global.AUTO_LABEL_NAMES[1]:
                att_id = l['id']
            elif l['name'] == Global.AUTO_LABEL_NAMES[2]:
                urg_id = l['id']

        for c in cards:
            try:
                company = Company.objects.get(card_id=c['id'])
            except Company.DoesNotExist:
                print('{} não presente no banco de dados!'.format(c['name']))
                continue

            card_labels = Helper.get_nested_objs('cards', c['id'], 'labels').json()

            right_label = company.status_label
            if right_label == Global.AUTO_LABEL_NAMES[0]:
                right_id = upd_id
            elif right_label == Global.AUTO_LABEL_NAMES[1]:
                right_id = att_id
            elif right_label == Global.AUTO_LABEL_NAMES[2]:
                right_id = urg_id

            found = False
            for cl in card_labels:
                if cl['name'] in Global.AUTO_LABEL_NAMES:
                    if cl['name'] != right_label:
                        Helper.delete_label(c['id'], cl['id'])
                    else:
                        found = True

            if not found:
                Helper.post_label(c['id'], right_id)

    @staticmethod
    def objs_update():
        # TODO
        return
