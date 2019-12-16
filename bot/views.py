from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from .forms import *
import os
from bot.models import Contractor, PostSeller
from trello_helper.models import Helper
import random as rd


def dashboard(request):
    pass


class NewCompany(View):
    form_class = NewCompanyForm
    template_name = 'new_company.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            seller = form.cleaned_data['seller']
            category = form.cleaned_data['category']
            main_contact = form.cleaned_data['main_contact']

            lists = Helper.get_nested_objs('boards', os.environ['SALES_BOARD_ID'], 'lists').json()
            for l in lists:
                if l['name'] == seller.name:
                    list_id = l['id']
                    break
            card_id = Helper.post_card(name, list_id).json()['id']

            Company(
                name=name,
                card_id=card_id,
                seller=seller,
                category=category,
                main_contact=main_contact,
            ).save()

            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class CloseCompany(View):
    form_class = CloseCompanyForm
    template_name = 'close_company.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            company = form.cleaned_data['originalcom']
            fee_type = form.cleaned_data['fee_type']
            contract_type = form.cleaned_data['contract_type']
            intake = form.cleaned_data['intake']

            cn = Contractor.objects.order_by('contact_count')[0].contact_count
            clist = Contractor.objects.filter(contact_count=cn)
            contractor = rd.choice(clist)

            pn = PostSeller.objects.order_by('contact_count')[0].contact_count
            plist = PostSeller.objects.filter(contact_count=pn)
            postseller = rd.choice(plist)

            lists = Helper.get_nested_objs(
                'boards', os.environ['CONTRACTS_BOARD_ID'], 'lists').json()
            for l in lists:
                if l['name'] == contractor.name:
                    list_id = l['id']
                    break
            card_id = Helper.post_card(name, list_id).json()['id']

            ClosedCompany(
                originalcom=company,
                sec_card_id=card_id,
                contractor=contractor,
                postseller=postseller,
                fee_type=fee_type,
                contract_type=contract_type,
                intake=intake,
            ).save()

            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class EditCompany(View):
    form_class = EditCompanyForm
    initial = {'key': 'value'}
    template_name = 'edit_company.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class NewHunter(View):
    form_class = NewHunterForm
    template_name = 'new_hunter.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            hunter_type = form.cleaned_data['hunter_type']

            if hunter_type == 'S':
                list_id = Helper.post_list(name, os.environ['SALES_BOARD_ID']).json()['id']
                Seller(name, email, list_id).save()
            elif hunter_type == 'C':
                list_id = Helper.post_list(name, os.environ['CONTRACTS_BOARD_ID']).json()['id']
                Contractor(name, email, list_id).save()
            else:
                PostSeller(name, email).save()

            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


class EditHunter(View):
    form_class = EditHunterForm
    initial = {'key': 'value'}
    template_name = 'edit_hunter.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})


def favicon(request):
    return HttpResponse(status=200)
