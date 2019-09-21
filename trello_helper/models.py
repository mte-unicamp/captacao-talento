from django.db import models
# import requests as re
# import json


class Helper(models.Model):
    """docstring for Helper"""

    api_url = "https://api.trello.com/1"
    board_id = models.CharField(max_length=100)

    @classmethod
    def generic_request(ext_obj, obj_id, nested_obj):
        # TODO
        return  # url, querystring

    @classmethod
    def get_nested_objs(ext_obj, obj_id, nested_obj=''):
        # TODO
        return  # response

    @classmethod
    def post_label(card_id, label):
        # TODO
        return

    @classmethod
    def delete_label(card_id, label_id):
        # TODO
        return


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
