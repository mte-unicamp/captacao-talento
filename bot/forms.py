from django import forms
from bot.models import Company, Seller, Contractor, PostSeller
from globalvars.models import Global


type_choices = (
    ('V', 'Vendedor'),
    ('C', 'Financeiro'),
    ('P', 'Pós-Venda'),
)


class EmptyChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):

        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u'', empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(
            choices=choices,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            *args, **kwargs
        )


class NewCompanyForm(forms.Form):

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)
    seller = forms.ModelChoiceField(queryset=Seller.objects.all())
    main_contact = forms.EmailField(required=False)


class CloseCompanyForm(forms.Form):

    originalcom = forms.ModelChoiceField(queryset=Company.objects.exclude(seller_stage=Global.CLOS))
    fee_type = forms.ChoiceField(choices=Global.FEE_TYPE_CHOICES)
    contract_type = forms.ChoiceField(choices=Global.CONTRACT_TYPE_CHOICES)
    intake = forms.IntegerField()


class EditCompanyForm(forms.Form):

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)
    main_contact = forms.EmailField(required=False)
    seller_stage = forms.ChoiceField(
        choices=Global.STAGE_SELLER_CHOICES,
        help_text='Só edite se souber o que está fazendo'
    )

    seller = forms.ModelChoiceField(queryset=Seller.objects.all())
    contractor = forms.ModelChoiceField(queryset=Contractor.objects.all(), required=False)
    postseller = forms.ModelChoiceField(queryset=PostSeller.objects.all(), required=False)

    fee_type = EmptyChoiceField(
        choices=Global.FEE_TYPE_CHOICES,
        required=False,
        empty_label='-----'
    )
    contract_type = EmptyChoiceField(
        choices=Global.CONTRACT_TYPE_CHOICES,
        required=False,
        empty_label='-----'
    )
    intake = forms.IntegerField(required=False)
    payment_form = EmptyChoiceField(
        choices=Global.PAYMENT_FORM_CHOICES,
        required=False,
        empty_label='-----'
    )
    payday = forms.DateField(widget=forms.SelectDateWidget, required=False)
    stand_size = forms.IntegerField(required=False)
    stand_pos = forms.CharField(max_length=10, required=False)
    custom_stand = forms.BooleanField(required=False)
    needs_receipt = forms.BooleanField(required=False)


class NewHunterForm(forms.Form):

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    hunter_type = forms.ChoiceField(choices=type_choices)


class EditHunterForm(forms.Form):

    email = forms.EmailField()
    hunter_type = forms.ChoiceField(choices=type_choices)
