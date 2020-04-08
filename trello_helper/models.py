from django.db import models
import os
import requests as rq
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
        return rq.get(url, params=querystring)

    @staticmethod
    def post_card(name, list_id):
        url = f'{Helper.api_url}/cards'
        querystring = {
            'name': name,
            'idList': list_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return rq.post(url, params=querystring)

    @staticmethod
    def post_list(name, board_id):
        url = f'{Helper.api_url}/lists'
        querystring = {
            'name': name,
            'idBoard': board_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return rq.post(url, params=querystring)

    @staticmethod
    def put_card_in_list(card_id, list_id):
        url = f'{Helper.api_url}/cards/{card_id}'
        querystring = {
            'idList': list_id,
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return rq.put(url, params=querystring)

    @staticmethod
    def post_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        querystring.update({'value': label_id})
        return rq.post(url, params=querystring)

    @staticmethod
    def delete_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        url = '{}/{}'.format(url, label_id)
        return rq.delete(url, params=querystring)


class Updater(models.Model):
    """docstring for Updater"""

    @staticmethod
    def set_last_activity(company):
        progress_graph = {
            Global.FIRS: [Global.NANS, Global.INTE, Global.NEGO, Global.REJE, Global.CLOS],
            Global.NANS: [Global.INTE, Global.NEGO, Global.REJE, Global.CLOS],
            Global.INTE: [Global.NANS, Global.NEGO, Global.REJE, Global.CLOS],
            Global.NEGO: [Global.NANS, Global.REJE, Global.CLOS],
        }
        stage = company.seller_stage
        if stage in progress_graph.keys():
            try:
                card = Helper.get_nested_objs('cards', company.card_id).json()
            except:
                print('{} não presente no quadro!'.format(company.name))
                return
            labels = card['labels']
            labels_names = [i['name'] for i in labels if i['name'] in Global.MANUAL_LABEL_NAMES.keys()]

            if not labels_names:
                all_labels = Helper.get_nested_objs('boards', os.environ['SALES_BOARD_ID'], 'labels').json()
                reverse_manual_label_names = {k: v for v, k in Global.MANUAL_LABEL_NAMES.items()}
                for l in all_labels:
                    if l['name'] == reverse_manual_label_names[Global.FIRS]:
                        label_id = l['id']
                        break
                Helper.post_label(card['id'], label_id)

            for l in labels_names:
                if Global.MANUAL_LABEL_NAMES[l] in progress_graph[stage]:
                    company.update()
                    company.seller_stage = Global.MANUAL_LABEL_NAMES[l]
                    company.save()
                    break

            if card['badges']['comments'] > company.comments_number:
                company.update()
                company.comments_number = card['badges']['comments']
                company.save()

    @staticmethod
    def label_update(board_id):

        cards = Helper.get_nested_objs('boards', board_id, 'cards').json()
        labels = Helper.get_nested_objs('boards', board_id, 'labels').json()

        for l in labels:
            if l['name'] == Global.AUTO_LABEL_NAMES[0]:
                upd_id = l['id']    # id for updated label
            elif l['name'] == Global.AUTO_LABEL_NAMES[1]:
                att_id = l['id']    # id for attention label
            elif l['name'] == Global.AUTO_LABEL_NAMES[2]:
                urg_id = l['id']    # id for urgent label

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
    def assign_new_hunter(company, hunter):

        if type(hunter) != PostSeller:
            r = Helper.put_card_in_list(company.card_id, hunter.list_id)
            if r.status_code != 200:
                raise r

        Reminder.new_company_reminder(company, hunter)

        if type(hunter) == Seller:
            company.seller = hunter
        elif type(hunter) == Contractor:
            company.closedcom.contractor = hunter
        elif type(hunter) == PostSeller:
            company.closedcom.postseller = hunter
        else:
            raise TypeError('Hunter must be Seller, Contractor or PostSeller')

        company.save()
        company.update()
