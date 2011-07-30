import re
from django import forms

from .models import Report


GITHUB_REGEXP = re.compile(r'^https:\/\/github.com\/[-\w]+\/[-.\w]+$')


class ReportForm(forms.ModelForm):

    url = forms.URLField(
        initial = 'https://github.com/',
        widget = forms.TextInput(attrs={'class': 'url-field'}),
    )

    class Meta:
        model = Report
        fields = ['url']

    def clean_url(self):
        url = self.cleaned_data['url']
        if not re.match(GITHUB_REGEXP, url):
            raise forms.ValidationError(u'Enter valid github repository url')
        return url
