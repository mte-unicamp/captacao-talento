from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
# Project
from bot.forms import (
    NewCompanyForm,
    CloseCompanyForm,
    EditCompanyForm,
    NewHunterForm,
    EditHunterForm,
)
from bot.models import (
    Seller,
    Contractor,
    PostSeller,
    Company,
    ClosedCompany,
    Reminder,
)
from trello_helper.models import Helper, Updater
from globalvars.models import Global
# Python
import os
import random as rd
import urllib.parse
# Google Sheets API
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


common_context = {
    'contact': os.environ['CONTACT'],
    'sales_board_url': os.environ['SALES_BOARD_URL'],
    'contracts_board_url': os.environ['CONTRACTS_BOARD_URL'],
    'contacts_table_url': os.environ['CONTACTS_TABLE_URL'],
    'manual_url': os.environ['MANUAL_URL'],
    'proposal_url': os.environ['PROPOSAL_URL'],
    'media_kit_url': os.environ['MEDIA_KIT_URL'],
    'email_model_url': os.environ['EMAIL_MODEL_URL'],
}


def dashboard(request):
    title = 'Dashboard'
    template_name = 'index.html'
    counters = {
        'total_contact': Company.objects.all().count(),
        'total_closed': Company.objects.filter(seller_stage=Global.CLOS).count(),
    }
    fee = {
        'diamond': ClosedCompany.objects.filter(fee_type=Global.DIAM).count(),
        'gold': ClosedCompany.objects.filter(fee_type=Global.GOLD).count(),
        'silver': ClosedCompany.objects.filter(fee_type=Global.SILV).count(),
        'bronze': ClosedCompany.objects.filter(fee_type=Global.BRON).count(),
    }
    categories = {
        'labels': list(dict(Global.CATEGORY_CHOICES).values()),
        'data': [Company.objects.filter(
            category=i, seller_stage=Global.CLOS).count() for i in Global.CATEGORY_LIST],
    }
    closed_months = {
        'regulars': [
            ClosedCompany.objects.filter(
                date_closed__month=i,
                contract_type=Global.REGU
            ).count() for i in range(1, 8)
        ],
        'startups': [
            ClosedCompany.objects.filter(
                date_closed__month=i,
                contract_type=Global.STAR
            ).count() for i in range(1, 8)
        ],
    }

    return render(request, template_name, {
        **common_context,
        'page_name': title,
        'counters': counters,
        'fee': fee,
        'categories': categories,
        'closed_months': closed_months,
        'dashboard': True,
    })


class NewCompany(View):
    form_class = NewCompanyForm
    template_name = 'new_company.html'
    title = 'Inclusão de Empresa'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            **common_context,
            'page_name': self.title,
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
                return HttpResponse('No Trello list matches the seller. \
                    Please solve this issue before adding new company')
            card_id = Helper.post_card(name, list_id).json()['id']

            c = Company(
                name=name,
                card_id=card_id,
                seller=seller,
                category=category,
                main_contact=main_contact,
            )

            labels = Helper.get_nested_objs('boards', os.environ['SALES_BOARD_ID'], 'labels').json()
            reverse_manual_label_names = {k: v for v, k in Global.MANUAL_LABEL_NAMES.items()}
            for l in labels:
                if l['name'] == reverse_manual_label_names[Global.FIRS]:
                    label_id = l['id']
                    break
            Helper.post_label(card_id, label_id)

            c.save()

            return HttpResponseRedirect(f'/bot/new_company/{c.slug}/success/')

        return HttpResponse('Something went wrong')


def get_least_contractor():
    cn = sorted(Contractor.objects.all(), key=lambda x: x.contact_count)[0].contact_count
    clist = list(filter(lambda x: x.contact_count == cn, Contractor.objects.all()))
    return rd.choice(clist)


def get_least_postseller():
    pn = sorted(PostSeller.objects.all(), key=lambda x: x.contact_count)[0].contact_count
    plist = list(filter(lambda x: x.contact_count == pn, PostSeller.objects.all()))
    return rd.choice(plist)


def update_sheet(company):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = os.environ['CLOSED_TABLE_ID']
    RANGE_NAME = os.environ['CLOSED_TABLE_RANGE']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    new_row = [
        company.name,
        dict(Global.CATEGORY_CHOICES).get(company.category, ''),
        company.main_contact,
        company.seller.name,
        company.closedcom.contractor.name,
        company.closedcom.postseller.name,
        dict(Global.FEE_TYPE_CHOICES).get(company.closedcom.fee_type, ''),
        dict(Global.CONTRACT_TYPE_CHOICES).get(company.closedcom.contract_type, ''),
        company.closedcom.intake,
        dict(Global.PAYMENT_FORM_CHOICES).get(company.closedcom.payment_form, ''),
        company.closedcom.payday.strftime("%d/%m/%Y") if company.closedcom.payday else None,
        company.closedcom.stand_size,
        company.closedcom.stand_pos,
        company.closedcom.custom_stand,
        company.closedcom.needs_receipt,
    ]
    for i in range(len(values)):
        if values[i][0] == company.name:
            values[i] = new_row
            break
    else:
        values.append(new_row)

    body = {'values': values}
    result = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                   range=RANGE_NAME,
                                   valueInputOption='USER_ENTERED',
                                   body=body).execute()
    return


class CloseCompany(View):
    form_class = CloseCompanyForm
    template_name = 'close_company.html'
    title = 'Fechamento de Empresa'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            **common_context,
            'page_name': self.title,
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

            contractor = get_least_contractor()
            postseller = get_least_postseller()

            lists = Helper.get_nested_objs(
                'boards', os.environ['CONTRACTS_BOARD_ID'], 'lists').json()
            for l in lists:
                if l['name'] == contractor.name:
                    list_id = l['id']
                    break
            card_id = Helper.post_card(company.name, list_id).json()['id']

            cc = ClosedCompany(
                originalcom=company,
                sec_card_id=card_id,
                contractor=contractor,
                postseller=postseller,
                fee_type=fee_type,
                contract_type=contract_type,
                intake=intake,
            )

            Reminder.new_company_reminder(company, contractor)
            Reminder.new_company_reminder(company, postseller)

            company.seller_stage = Global.CLOS
            company.closedcom = cc

            labels = Helper.get_nested_objs('boards', os.environ['SALES_BOARD_ID'], 'labels').json()
            reverse_manual_label_names = {k: v for v, k in Global.MANUAL_LABEL_NAMES.items()}
            for l in labels:
                if l['name'] == reverse_manual_label_names[Global.CLOS]:
                    label_id = l['id']
                    break
            Helper.post_label(company.card_id, label_id)

            update_sheet(company)

            cc.save()
            company.save()

            return HttpResponseRedirect(f'/bot/close_company/{company.slug}/success/')

        return HttpResponse('Something went wrong')


class SelectCompany(View):
    template_name = 'select_company.html'
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
            **common_context,
            'page_name': self.title,
            'edit_company': True,
            'companies': companies,
        })


class EditCompany(View):
    form_class = EditCompanyForm
    template_name = 'edit_company.html'
    title = 'Edição de {}'

    def get_company(self, name):
        try:
            c = Company.objects.get(name=name)
        except Company.DoesNotExist:
            c = Company.objects.get(name=name.replace('-', ' '))
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
            **common_context,
            'page_name': self.title.format(name),
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
            if c.seller != form.cleaned_data['seller']:
                Updater.assign_new_hunter(c, form.cleaned_data['seller'])
            if form.cleaned_data['main_contact'] != '':
                c.main_contact = form.cleaned_data['main_contact']

            if c.seller_stage == Global.CLOS:
                # contract info
                if cc.contractor != form.cleaned_data['contractor']:
                    Updater.assign_new_hunter(c, form.cleaned_data['contractor'])
                if cc.postseller != form.cleaned_data['postseller']:
                    Updater.assign_new_hunter(c, form.cleaned_data['postseller'])
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

                update_sheet(c)

            c.save()

            return HttpResponseRedirect(f'/bot/edit_company/{c.slug}/success/')

        return HttpResponse('Something went wrong')


def create_hunter(name, email, hunter_type):
    if hunter_type == 'V':
        list_id = Helper.post_list(name, os.environ['SALES_BOARD_ID']).json()['id']
        h = Seller(name=name, email=email, list_id=list_id)
        h.save()
    elif hunter_type == 'C':
        list_id = Helper.post_list(name, os.environ['CONTRACTS_BOARD_ID']).json()['id']
        h = Contractor(name=name, email=email, list_id=list_id)
        h.save()
    else:
        h = PostSeller(name=name, email=email)
        h.save()
    return h


class NewHunter(View):
    form_class = NewHunterForm
    template_name = 'new_hunter.html'
    title = 'Inclusão de Captador'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {
            **common_context,
            'page_name': self.title,
            'new_hunter': True,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            h = create_hunter(
                form.cleaned_data['name'],
                form.cleaned_data['email'],
                form.cleaned_data['hunter_type']
            )

            return HttpResponseRedirect(f'/bot/new_hunter/{h.slug}/success/')

        return HttpResponse('Something went wrong')


class SelectHunter(View):
    template_name = 'select_hunter.html'
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
            **common_context,
            'page_name': self.title,
            'edit_hunter': True,
            'hunters': hunters,
        })


class EditHunter(View):

    form_class = EditHunterForm
    template_name = 'edit_hunter.html'
    title = 'Edição de {}'

    def get_hunter(self, pk):
        pk = pk.replace('-', ' ')
        pk = urllib.parse.unquote(pk)
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
            **common_context,
            'page_name': self.title.format(h.name),
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
                new = create_hunter(h.name, h.email, hunter_type)
                companies = h.contact_list
                h.delete()
                for c in companies:
                    contractor = get_least_contractor()
                    postseller = get_least_postseller()
                    Updater.assign_new_hunter(c, contractor)
                    Updater.assign_new_hunter(c, postseller)
                h = new
            else:
                h.save()

            return HttpResponseRedirect(f'/bot/edit_hunter/{h.slug}/success/')

        return HttpResponse('Something went wrong')


def success(request, verb, nom, name):
    name = name.replace('-', ' ')
    action = {}
    action['title'] = []

    if verb == 'new':
        action['title'].append('Inclusão')
        action['infinitive'] = 'Adicionar'
        action['past'] = 'adicionado(a)'
    elif verb == 'edit':
        action['title'].append('Edição')
        action['infinitive'] = 'Editar'
        action['past'] = 'editado(a)'
    elif verb == 'close':
        action['title'].append('Fechamento')
        action['infinitive'] = 'Fechar'
        action['past'] = 'fechada'

    hunter = False
    if nom == 'company':
        action['title'].append('Empresa')
    elif nom == 'hunter':
        action['title'].append('Captador')
        hunter = True

    verb = 'select' if verb == 'edit' else verb

    title = ' de '.join(action['title'])
    template_name = 'success.html'

    return render(request, template_name, {
        **common_context,
        'page_name': title,
        'name': name,
        'action': action,
        'link': f'/bot/{verb}_{nom}/',
        'hunter': hunter,
    })


def closed_companies(request):
    title = 'Empresas Fechadas'
    template_name = 'closed_companies.html'

    return render(request, template_name, {
        **common_context,
        'page_name': title,
        'closed_companies': True,
        'closed_table_url': os.environ['CLOSED_TABLE_URL'],
    })


def favicon(request):
    return HttpResponse(status=200)
