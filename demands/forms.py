from django import forms


class DemandAddForm(forms.Form):
    address = forms.CharField(max_length=100)
    load = forms.IntegerField()
