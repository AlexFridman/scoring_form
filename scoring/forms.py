from django import forms

from scoring.models import ScoringInfo


class ScoringForm(forms.ModelForm):
    class Meta:
        model = ScoringInfo
        widgets = {
            'application_id': forms.HiddenInput(),
            'repayment_prob': forms.HiddenInput()
        }
        fields = '__all__'
