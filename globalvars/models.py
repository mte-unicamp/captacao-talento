from django.db import models


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
    CONC = 'conc'
    RECR = 'recr'
    RESE = 'rese'

    CATEGORY_LIST = [FINA, CONS, TECH, COMM, HEAL, MANU, CONC, RECR, RESE]

    CATEGORY_CHOICES = [
        (FINA, 'Financial'), (CONS, 'Consulting'),
        (TECH, 'Technology'), (COMM, 'Communication'),
        (HEAL, 'Health'), (MANU, 'Manufacturing'), (CONC, 'Construction'),
        (RECR, 'Recruiting'), (RESE, 'Research'),
    ]

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

    STAGE_SELLER_CHOICES = [
        (FIRS, 'Initial Contact'), (NANS, 'No Answer'), (INTE, 'Interested'),
        (REJE, 'Rejected'), (NEGO, 'Negotiation'), (CLOS, 'Closed'),
    ]

    FEE_TYPE_CHOICES = [
        (BRON, 'Bronze'), (SILV, 'Silver'), (GOLD, 'Gold'),
        (DIAM, 'Diamond'), (OTHE, 'Other'),
    ]

    CONTRACT_TYPE_CHOICES = [
        (REGU, 'Regular'), (STAR, 'Startup'), (CANC, 'Cancelled'),
    ]

    PAYMENT_FORM_CHOICES = [
        (BOLE, 'Boleto'), (TRAN, 'Transfer'),
    ]

    AUTO_LABEL_NAMES = ['Atualizado', 'Atenção', 'Urgente']

    MANUAL_LABEL_NAMES = {'Contato Inicial': FIRS, 'Sem Resposta': NANS,
                          'Interessada': INTE, 'Rejeitado': REJE,
                          'Negociação': NEGO, 'Fechada': CLOS}

    # deadline variables
    ATTENTION_DEADLINE = models.IntegerField(default=8)
    URGENT_DEADLINE = models.IntegerField(default=15)
