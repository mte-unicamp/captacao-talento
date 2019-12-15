from django import forms
from bot.models import Company, ClosedCompany, Hunter


class NewCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'seller', 'category', 'main_contact']


class CloseCompanyForm(forms.ModelForm):

    company = forms.ModelChoiceField(queryset=Company.objects.all())
    """
    class Meta:
        model = ClosedCompany
        fields = ['company', 'fee_type', 'contract_type',
                  'payment_form', 'intake', 'needs_receipt', 'stand_size',
                  'stand_pos', 'custom_stand', 'payday',
                 ]
    """


class EditCompanyForm(forms.ModelForm):
    """
    class Meta:
        model = ClosedCompany
        fields = ['name', 'seller', 'category', 'company', 'fee_type',
                  'contract_type', 'payment_form', 'intake', 'needs_receipt',
                  'stand_size', 'stand_pos', 'custom_stand', 'payday']
    """


class NewHunterForm(forms.ModelForm):
    class Meta:
        model = Hunter
        fields = ['name', 'email']


class EditHunterForm(forms.ModelForm):
    class Meta:
        model = Hunter
        fields = ['name', 'email']
