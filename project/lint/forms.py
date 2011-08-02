from django import forms
from .models import Report


class ReportForm(forms.ModelForm):

    url = forms.URLField(
        initial = 'https://github.com/',
        widget = forms.TextInput(attrs={'class': 'url-field'}),
    )

    class Meta:
        model = Report
        fields = ['url']
