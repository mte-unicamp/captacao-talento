from django.db import models


class Global(models.Model):
    """
    Set of global variabels used by other models
    """

    # Categories
    FINA = 'fina'
    CONS = 'cons'
    TECH = 'tech'
    COMM = 'comm'
    HEAL = 'heal'
    MANU = 'manu'
    CONC = 'conc'
    RECR = 'recr'
    RESE = 'rese'
    RETA = 'reta'
    SERV = 'serv'

    CATEGORY_LIST = [FINA, CONS, TECH, COMM, HEAL, MANU, CONC, RECR, RESE, RETA, SERV]

    CATEGORY_CHOICES = [
        (FINA, 'Financial'), (CONS, 'Consulting'),
        (TECH, 'Technology'), (COMM, 'Communication'),
        (HEAL, 'Health'), (MANU, 'Manufacturing'), (CONC, 'Construction'),
        (RECR, 'Recruiting'), (RESE, 'Research'),
        (RETA, 'Retail'), (SERV, 'Services'),
    ]

    # Seller stages
    FIRS = 'firs'
    NANS = 'nans'
    INTE = 'inte'
    REJE = 'reje'
    NEGO = 'nego'
    CLOS = 'clos'

    STAGE_SELLER_LIST = [FIRS, NANS, INTE, REJE, NEGO, CLOS]

    STAGE_SELLER_CHOICES = [
        (FIRS, 'Initial Contact'), (NANS, 'No Answer'), (INTE, 'Interested'),
        (REJE, 'Rejected'), (NEGO, 'Negotiation'), (CLOS, 'Closed'),
    ]

    NO_REMINDER = [NANS, REJE, CLOS]

    # Fee type
    BRON = 'bron'
    SILV = 'silv'
    GOLD = 'gold'
    DIAM = 'diam'
    OTHE = 'othe'

    FEE_TYPE_LIST = [BRON, SILV, GOLD, DIAM, OTHE]

    FEE_TYPE_CHOICES = [
        (BRON, 'Bronze'), (SILV, 'Silver'), (GOLD, 'Gold'),
        (DIAM, 'Diamond'), (OTHE, 'Other'),
    ]

    # Contract type
    REGU = 'regu'
    STAR = 'star'
    CANC = 'canc'

    CONTRACT_TYPE_LIST = [REGU, STAR, CANC]

    CONTRACT_TYPE_CHOICES = [
        (REGU, 'Regular'), (STAR, 'Startup'), (CANC, 'Cancelled'),
    ]

    # Payment form
    BOLE = 'bole'
    TRAN = 'tran'

    PAYMENT_FORM_LIST = [BOLE, TRAN]

    PAYMENT_FORM_CHOICES = [
        (BOLE, 'Boleto'), (TRAN, 'Transfer'),
    ]

    # Trello Board Ref

    AUTO_LABEL_NAMES = ['Atualizado', 'Atenção', 'Urgente']

    MANUAL_LABEL_NAMES = {'Contato Inicial': FIRS, 'Sem Resposta': NANS,
                          'Interessada': INTE, 'Rejeitado': REJE,
                          'Negociação': NEGO, 'Fechada': CLOS}

    # deadline variables
    ATTENTION_DEADLINE = models.IntegerField(default=8)
    URGENT_DEADLINE = models.IntegerField(default=15)
