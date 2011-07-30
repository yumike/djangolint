import re
from django import forms

from .models import Report


GITHUB_REGEXP = re.compile(r'^https:\/\/github.com\/[-\w]+\/[-\w]+\.git$')


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ['url']

    def clean_url(self):
        url = cleaned_data['url']
        if not re.match(GITHUB_REGEXP, url):
            raise forms.ValidationError(u'Enter valid github repository url')
        return url
