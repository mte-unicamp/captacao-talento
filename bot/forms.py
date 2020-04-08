# Django
from django import forms
from django_select2.forms import ModelSelect2Widget

# Project
from bot.models import Company, Contractor, PostSeller, Seller
from globalvars.models import Global


type_choices = (
    ("V", "Vendedor"),
    ("C", "Financeiro"),
    ("P", "Pós-Venda"),
)


class EmptyChoiceField(forms.ChoiceField):
    def __init__(
        self,
        choices=(),
        empty_label=None,
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text=None,
        *args,
        **kwargs
    ):

        # prepend an empty label if it exists (and field is not required!)
        if not required and empty_label is not None:
            choices = tuple([(u"", empty_label)] + list(choices))

        super(EmptyChoiceField, self).__init__(
            choices=choices,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            *args,
            **kwargs
        )


class NewCompanyForm(forms.Form):

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)
    seller = forms.ModelChoiceField(queryset=Seller.objects.all().order_by("name"))
    main_contact = forms.EmailField(required=False)


class CloseCompanyForm(forms.Form):

    originalcom = forms.ModelChoiceField(
        widget=ModelSelect2Widget(model=Company, search_fields=["name__icontains"]),
        queryset=Company.objects.exclude(seller_stage=Global.CLOS).order_by("name"),
    )
    fee_type = forms.ChoiceField(choices=Global.FEE_TYPE_CHOICES)
    contract_type = forms.ChoiceField(choices=Global.CONTRACT_TYPE_CHOICES)
    intake = forms.IntegerField()


class EditCompanyForm(forms.Form):

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)
    main_contact = forms.EmailField(required=False)
    seller_stage = forms.ChoiceField(
        choices=Global.STAGE_SELLER_CHOICES,
        help_text="Só edite se souber o que está fazendo. Se não souber, edite no Trello!",
    )

    seller = forms.ModelChoiceField(queryset=Seller.objects.all().order_by("name"))
    contractor = forms.ModelChoiceField(
        queryset=Contractor.objects.all().order_by("name"), required=False
    )
    postseller = forms.ModelChoiceField(
        queryset=PostSeller.objects.all().order_by("name"), required=False
    )

    fee_type = EmptyChoiceField(
        choices=Global.FEE_TYPE_CHOICES, required=False, empty_label="-----"
    )
    contract_type = EmptyChoiceField(
        choices=Global.CONTRACT_TYPE_CHOICES, required=False, empty_label="-----"
    )
    intake = forms.IntegerField(required=False)
    payment_form = EmptyChoiceField(
        choices=Global.PAYMENT_FORM_CHOICES, required=False, empty_label="-----"
    )
    payday = forms.DateField(
        input_formats=["%d/%m/%Y"],
        widget=forms.DateTimeInput(
            attrs={"class": "form-control datetimepicker-input", "data-target": "#datetimepicker4"}
        ),
        required=False,
    )
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
