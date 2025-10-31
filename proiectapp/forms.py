from django import forms
from .models import Categorie, Producator, Seria, Figurina

class FigurinaFiltruForm(forms.Form):
    nume_figurina = forms.forms.CharField(
        label ='Nume',
        required = False,
        widget=forms.TextInput(attrs={'placeholder': 'Cautare dupa nume: '})
        )
    pret_min = forms.DecimalField(
        
    )