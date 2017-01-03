from django import forms

from scoring.models import ScoringInfo


class ScoringForm(forms.ModelForm):
    class Meta:
        model = ScoringInfo
        widgets = {
            'credit_amount': forms.HiddenInput(),
            'duration_in_month': forms.HiddenInput(),
            'age': forms.HiddenInput(),
            'request_id': forms.HiddenInput()
        }
        fields = '__all__'
