from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from .forms import *
import os
from bot.models import *
from trello_helper.models import Helper
import random as rd
import datetime


contact = os.environ['CONTACT']


def dashboard(request):
    title = 'Dashboard'
    total_contact = Company.objects.all().count()
    total_closed = Company.objects.filter(seller_stage=Global.CLOS).count()
    diamond = ClosedCompany.objects.filter(fee_type=Global.DIAM).count()
    gold = ClosedCompany.objects.filter(fee_type=Global.GOLD).count()
    silver = ClosedCompany.objects.filter(fee_type=Global.SILV).count()
    bronze = ClosedCompany.objects.filter(fee_type=Global.BRON).count()
    categories = {
        'labels': list(dict(Global.CATEGORY_CHOICES).values()),
        'data': [Company.objects.filter(category=i).count() for i in Global.CATEGORY_LIST],
    }
    regulars = {}
    startups = {}
    regulars['months'] = [
        ClosedCompany.objects.filter(
            date_closed__month=i,
            contract_type=Global.REGU
        ).count() for i in range(1, 8)
    ]
    startups['months'] = [
        ClosedCompany.objects.filter(
            date_closed__month=i,
            contract_type=Global.STAR
        ).count() for i in range(1, 8)
    ]
    earliest_date = ClosedCompany.objects.all().order_by('date_closed')[0].date_closed
    earliest_date = earliest_date -datetime.timedelta(days=1)
    days = (datetime.date.today() - earliest_date).days
    regulars['labels'] = [
        (earliest_date + datetime.timedelta(days=i)).strftime("%d/%m") for i in range(days)
    ]
    regulars['days'] = [
        ClosedCompany.objects.filter(
            date_closed=earliest_date + datetime.timedelta(days=i),
            contract_type=Global.REGU
        ).count() for i in range(days)
    ]
    startups['days'] = [
        ClosedCompany.objects.filter(
            date_closed=earliest_date + datetime.timedelta(days=i),
            contract_type=Global.STAR
        ).count() for i in range(days)
    ]
    return render(request, 'bot/index.html', {
        'page_name': title,
        'contact': contact,
        'total_contact': total_contact,
        'total_closed': total_closed,
        'diamond': diamond,
        'gold': gold,
        'silver': silver,
        'bronze': bronze,
        'categories': categories,
        'regulars': regulars,
        'startups': startups,
        'dashboard': True,
    })


class NewCompany(View):
    form_class = NewCompanyForm
    template_name = 'bot/new_company.html'
    title = 'Inclusão de Empresa'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'page_name': self.title,
            'contact': contact,
            'new_company': True,
            'form': form,
        })

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
            else:
                # PROBLEM: no list matches the seller
                pass
            card_id = Helper.post_card(name, list_id).json()['id']

            Company(
                name=name,
                card_id=card_id,
                seller=seller,
                category=category,
                main_contact=main_contact,
            ).save()

            return HttpResponseRedirect('/bot/new_company/success/')

        return HttpResponse('Something went wrong')


class CloseCompany(View):
    form_class = CloseCompanyForm
    template_name = 'bot/close_company.html'
    title = 'Fechamento de Empresa'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'page_name': self.title,
            'contact': contact,
            'close_company': True,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            company = form.cleaned_data['originalcom']
            fee_type = form.cleaned_data['fee_type']
            contract_type = form.cleaned_data['contract_type']
            intake = form.cleaned_data['intake']

            cn = sorted(Contractor.objects.all(), key=lambda x: x.contact_count)[0].contact_count
            clist = list(filter(lambda x: x.contact_count == cn, Contractor.objects.all()))
            contractor = rd.choice(clist)

            pn = sorted(PostSeller.objects.all(), key=lambda x: x.contact_count)[0].contact_count
            plist = list(filter(lambda x: x.contact_count == pn, PostSeller.objects.all()))
            postseller = rd.choice(plist)

            lists = Helper.get_nested_objs(
                'boards', os.environ['CONTRACTS_BOARD_ID'], 'lists').json()
            for l in lists:
                if l['name'] == contractor.name:
                    list_id = l['id']
                    break
            card_id = Helper.post_card(company.name, list_id).json()['id']

            c = ClosedCompany(
                originalcom=company,
                sec_card_id=card_id,
                contractor=contractor,
                postseller=postseller,
                fee_type=fee_type,
                contract_type=contract_type,
                intake=intake,
            )

            c.save()

            company.seller_stage = Global.CLOS
            company.closedcom = c
            company.save()

            return HttpResponseRedirect('/bot/close_company/success/')

        return HttpResponse('Something went wrong')


class SelectCompany(View):
    template_name = 'bot/select_company.html'
    title = 'Seleção de Empresa'

    def get(self, request, *args, **kwargs):
        c_list = []
        cats = dict(Global.CATEGORY_CHOICES)
        stas = dict(Global.STAGE_SELLER_CHOICES)
        for i in Company.objects.all().order_by('name'):
            i.category = cats[i.category]
            i.seller_stage = stas[i.seller_stage]
            c_list.append(i)
        companies = {i + 1: j for i, j in enumerate(c_list)}
        return render(request, self.template_name, {
            'page_name': self.title,
            'contact': contact,
            'edit_company': True,
            'companies': companies,
        })


class EditCompany(View):
    form_class = EditCompanyForm
    template_name = 'bot/edit_company.html'
    title = 'Edição de {}'

    def get_company(self, name):
        name = name.replace('-', ' ')
        c = Company.objects.get(name=name)
        try:
            cc = ClosedCompany.objects.get(originalcom=c)
        except ClosedCompany.DoesNotExist:
            cc = None
        return c, cc

    def get(self, request, name, *args, **kwargs):
        c, cc = self.get_company(name)
        initial = {
            'name': c.name,
            'category': c.category,
            'main_contact': c.main_contact,
            'seller_stage': c.seller_stage,
            'seller': c.seller,
        }

        if cc is not None:
            initial.update({
                'contractor': cc.contractor,
                'postseller': cc.postseller,
                'fee_type': cc.fee_type,
                'contract_type': cc.contract_type,
                'intake': cc.intake,
                'payment_form': cc.payment_form,
                'payday': cc.payday.strftime("%d/%m/%Y") if cc.payday is not None else None,
                'stand_size': cc.stand_size,
                'stand_pos': cc.stand_pos,
                'custom_stand': cc.custom_stand,
                'needs_receipt': cc.needs_receipt,
            })

        form = self.form_class(initial=initial)
        return render(request, self.template_name, {
            'page_name': self.title.format(name),
            'contact': contact,
            'edit_company': True,
            'is_closed': c.seller_stage == Global.CLOS,
            'name': name,
            'form': form,
        })

    def post(self, request, name, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            c, cc = self.get_company(name)

            c.name = form.cleaned_data['name']
            c.category = form.cleaned_data['category']
            c.seller_stage = form.cleaned_data['seller_stage']
            c.seller = form.cleaned_data['seller']
            if form.cleaned_data['main_contact'] != '':
                c.main_contact = form.cleaned_data['main_contact']

            c.save()

            if c.seller_stage == Global.CLOS:
                # contract info
                cc.contractor = form.cleaned_data['contractor']
                cc.postseller = form.cleaned_data['postseller']
                cc.fee_type = form.cleaned_data['fee_type']
                cc.contract_type = form.cleaned_data['contract_type']
                cc.intake = form.cleaned_data['intake']

                if form.cleaned_data['payment_form'] != '':
                    cc.payment_form = form.cleaned_data['payment_form']
                if form.cleaned_data['payday'] != '':
                    cc.payday = form.cleaned_data['payday']
                cc.needs_receipt = form.cleaned_data['needs_receipt']

                # fair info
                if form.cleaned_data['stand_size'] is not None:
                    cc.stand_size = form.cleaned_data['stand_size']
                if form.cleaned_data['stand_pos'] != '':
                    cc.stand_pos = form.cleaned_data['stand_pos']
                cc.custom_stand = form.cleaned_data['custom_stand']

                cc.save()

            return HttpResponseRedirect(f'/bot/edit_company/{name}/success/')

        return HttpResponse('Something went wrong')


class NewHunter(View):
    form_class = NewHunterForm
    template_name = 'bot/new_hunter.html'
    title = 'Inclusão de Captador'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            'page_name': self.title,
            'contact': contact,
            'new_hunter': True,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            hunter_type = form.cleaned_data['hunter_type']

            if hunter_type == 'V':
                list_id = Helper.post_list(name, os.environ['SALES_BOARD_ID']).json()['id']
                Seller(
                    name=name,
                    email=email,
                    list_id=list_id
                ).save()
            elif hunter_type == 'C':
                list_id = Helper.post_list(name, os.environ['CONTRACTS_BOARD_ID']).json()['id']
                Contractor(
                    name=name,
                    email=email,
                    list_id=list_id
                ).save()
            else:
                PostSeller(
                    name=name,
                    email=email
                ).save()

            return HttpResponseRedirect('/bot/new_hunter/success/')

        return HttpResponse('Something went wrong')


class SelectHunter(View):
    template_name = 'bot/select_hunter.html'
    title = 'Seleção de Captador'

    def get(self, request, *args, **kwargs):
        sellers = [i for i in Seller.objects.all()]
        contractors = [i for i in Contractor.objects.all()]
        postsellers = [i for i in PostSeller.objects.all()]
        for i in sellers:
            i.category = 'Vendas'
        for i in contractors:
            i.category = 'Contratos'
        for i in postsellers:
            i.category = 'Pós-Venda'
        h_list = sorted(sellers + contractors + postsellers, key=lambda x: x.name)
        hunters = {i + 1: j for i, j in enumerate(h_list)}
        return render(request, self.template_name, {
            'page_name': self.title,
            'contact': contact,
            'edit_hunter': True,
            'hunters': hunters,
        })


class EditHunter(View):

    form_class = EditHunterForm
    template_name = 'bot/edit_hunter.html'
    title = 'Edição de {}'

    def get_hunter(self, pk):
        pk = pk.replace('-', ' ')
        if Seller.objects.filter(pk=pk).count() != 0:
            h = Seller.objects.get(pk=pk)
            h.hunter_type = 'V'
        elif Contractor.objects.filter(pk=pk).count() != 0:
            h = Contractor.objects.get(pk=pk)
            h.hunter_type = 'C'
        elif PostSeller.objects.filter(pk=pk).count() != 0:
            h = PostSeller.objects.get(pk=pk)
            h.hunter_type = 'P'

        return h

    def get(self, request, pk, *args, **kwargs):
        h = self.get_hunter(pk)
        form = self.form_class(initial={
            'email': h.email,
            'hunter_type': h.hunter_type,
        })
        return render(request, self.template_name, {
            'page_name': self.title.format(h.name),
            'contact': contact,
            'edit_hunter': True,
            'pk': pk,
            'form': form,
        })

    def post(self, request, pk, *args, **kwargs):
        h = self.get_hunter(pk)
        form = self.form_class(request.POST)
        if form.is_valid():
            h.email = form.cleaned_data['email']
            hunter_type = form.cleaned_data['hunter_type']

            if h.hunter_type != hunter_type:
                # TODO: del object and create new
                pass

            h.save()

            return HttpResponseRedirect(f'/bot/edit_hunter/{pk}/success/')

        return HttpResponse('Something went wrong')


def closed_companies(request):
    title = 'Empresas Fechadas'
    template_name = 'bot/closed_companies.html'

    return render(
        request,
        template_name,
        {
            'page_name': title,
            'closed_companies': True,
            'contact': contact,
        }
    )


def favicon(request):
    return HttpResponse(status=200)
