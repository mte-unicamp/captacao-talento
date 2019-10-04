from django.db import models
import os
import requests as re
# import json


class Helper(models.Model):
    """docstring for Helper"""

    api_url = "https://api.trello.com/1"
    board_id = models.CharField(max_length=100)

    @classmethod
    def generic_request(ext_obj, obj_id, nested_obj):
        url = '{}/{}/{}/{}'.format(Helper.api_url, ext_obj,
                                   obj_id, nested_obj)
        querystring = {
            'key': os.environ['TRELLO_KEY'],
            'token': os.environ['TRELLO_TOKEN'],
        }
        return url, querystring

    @classmethod
    def get_nested_objs(ext_obj, obj_id, nested_obj=''):
        url, querystring = Helper.generic_request(ext_obj, obj_id, nested_obj)
        return re.get(url, params=querystring)

    @classmethod
    def post_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        querystring.update({'value': label_id})
        return re.post(url, params=querystring)

    @classmethod
    def delete_label(card_id, label_id):
        url, querystring = Helper.generic_request('cards', card_id, 'idLabels')
        url = ''.join([url, '/{}'.format(label_id)])
        return re.delete(url, params=querystring)


class Updater(models.Model):
    """docstring for Updater"""

    @classmethod
    def label_update(board_id):
        # TODO
        return

    @classmethod
    def objs_update():
        # TODO
        return
