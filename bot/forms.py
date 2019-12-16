from django import forms
from bot.models import Company, ClosedCompany, Hunter
from globalvars.models import Global


type_choices = (
    ('S', 'Vendedor'),
    ('C', 'Contratante'),
    ('P', 'Pós-Venda'),
)


class NewCompanyForm(forms.ModelForm):

    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)

    class Meta:
        model = Company
        fields = ['name', 'seller', 'main_contact']


class CloseCompanyForm(forms.ModelForm):

    fee_type = forms.ChoiceField(choices=Global.FEE_TYPE_CHOICES)
    contract_type = forms.ChoiceField(choices=Global.CONTRACT_TYPE_CHOICES)

    class Meta:
        model = ClosedCompany
        fields = ['originalcom', 'intake']


class EditCompanyForm(forms.ModelForm):

    name = forms.CharField(max_length=100)
    seller = forms.ModelChoiceField(queryset=Company.objects.all())
    category = forms.ChoiceField(choices=Global.CATEGORY_CHOICES)
    main_contact = forms.EmailField()

    fee_type = forms.ChoiceField(choices=Global.FEE_TYPE_CHOICES)
    contract_type = forms.ChoiceField(choices=Global.CONTRACT_TYPE_CHOICES)
    payment_form = forms.ChoiceField(choices=Global.PAYMENT_FORM_CHOICES)

    class Meta:
        model = ClosedCompany
        fields = ['contractor', 'postseller', 'intake', 'needs_receipt',
                  'stand_size', 'stand_pos', 'custom_stand', 'payday']


class NewHunterForm(forms.ModelForm):

    hunter_type = forms.ChoiceField(choices=type_choices)

    class Meta:
        model = Hunter
        fields = ['name', 'email']


class EditHunterForm(forms.ModelForm):

    hunter_type = forms.ChoiceField(choices=type_choices)

    class Meta:
        model = Hunter
        fields = ['name', 'email']
