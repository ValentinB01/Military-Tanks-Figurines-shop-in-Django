from datetime import datetime
from django import forms
from .models import Categorie, Producator, Seria, Figurina, Material
from django.forms import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.mail import mail_admins
from django.utils.html import strip_tags
from .models import CustomUser
from .models import Promotie
import datetime
import re
import logging
from .models import (
    Categorie, Producator, Seria, Figurina, Material
)

logger = logging.getLogger(__name__)

class FigurinaFiltruForm(forms.Form):

    nume_figurina = forms.CharField(
        label='Nume',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Cauta dupa nume'})
    )
    
    pret_min = forms.DecimalField(
        label='Pret minim',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Pret min'})
    )
    pret_max = forms.DecimalField(
        label='Pret maxim',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Pret max'})
    )

    greutate_min = forms.DecimalField(
        label='Greutate minima (kg)',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Greutate min'})
    )
    greutate_max = forms.DecimalField(
        label='Greutate maxima (kg)',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Greutate max'})
    )
    
    data_lansare_min = forms.DateField(
        label='Lansat dupa data',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_lansare_max = forms.DateField(
        label='Lansat inainte de data',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    stare = forms.MultipleChoiceField(
        label='Stare produs',
        required=False,
        choices=Figurina.STARE_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    tara_origine = forms.MultipleChoiceField(
        label='Tara de origine',
        required=False,
        choices=Figurina.TARA_ORIGINE_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    
    ordonare = forms.ChoiceField(
        label='Ordoneaza dupa',
        required=False,
        choices=[
            ('nume_figurina', 'Nume (A-Z)'),
            ('-nume_figurina', 'Nume (Z-A)'),
            ('pret', 'Preț (Crescător)'),
            ('-pret', 'Preț (Descrescător)'),
            ('-data_adaugare', 'Cele mai noi'),
        ],
        widget=forms.Select
    )
    
    per_pagina = forms.ChoiceField(
        label='Produse pe pagina',
        required=False,
        choices=[
            ('5', '5 pe pagina'),
            ('10', '10 pe pagina'),
            ('20', '20 pe pagina'),
            ('50', '50 pe pagina'),
        ],
        initial='5',
        widget=forms.Select
    )

    id_categorie = forms.ModelMultipleChoiceField(
        label='Categorie',
        queryset=Categorie.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    id_producator = forms.ModelMultipleChoiceField(
        label='Producator',
        queryset=Producator.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    id_serie = forms.ModelMultipleChoiceField(
        label='Serie',
        queryset=Seria.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    materiale = forms.ModelMultipleChoiceField(
        label='Materiale',
        queryset=Material.objects.none(), 
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, **kwargs):
        self.categorie_preselectata = kwargs.pop('categorie_preselectata', None)
        super().__init__(*args, **kwargs)
        self.fields['id_categorie'].queryset = Categorie.objects.all()
        self.fields['id_producator'].queryset = Producator.objects.all()
        self.fields['id_serie'].queryset = Seria.objects.all()
        self.fields['materiale'].queryset = Material.objects.all()
        if self.categorie_preselectata:
            self.initial['id_categorie'] = self.categorie_preselectata
            self.fields['id_categorie'].widget = forms.HiddenInput(attrs={'readonly': 'readonly'})    
            
    def clean(self):
        cleaned_data = super().clean()
        
        pret_min = cleaned_data.get('pret_min')
        pret_max = cleaned_data.get('pret_max')
        
        greutate_min = cleaned_data.get('greutate_min')
        greutate_max = cleaned_data.get('greutate_max')
        
        data_min = cleaned_data.get('data_lansare_min')
        data_max = cleaned_data.get('data_lansare_max')

        if pret_min is not None and pret_max is not None:
            if pret_min > pret_max:
                raise ValidationError(
                    "Eroare: Pretul maxim nu poate fi mai mic decat pretul minim.",
                    code='pret_interval_invalid'
                )
        if greutate_min is not None and greutate_max is not None:
            if greutate_min > greutate_max:
                raise ValidationError(
                    "Eroare: Greutatea maxima nu poate fi mai mica decat greutatea minima.",
                    code='greutate_interval_invalid'
                )
        if data_min and data_max:
            if data_min > data_max:
                raise ValidationError(
                    "Eroare: Data 'Lansat dupa' nu poate fi mai recenta decât data 'Lansat inainte de'.",
                    code='data_interval_invalid'
                )
        if self.categorie_preselectata:
            submitted_categories = cleaned_data.get('id_categorie')
            
            if (not submitted_categories or 
                submitted_categories.count() != 1 or 
                submitted_categories.first() != self.categorie_preselectata):
                
                raise ValidationError(
                    f"A fost detectata o nepotrivire. Acest filtru este valabil doar pentru categoria '{self.categorie_preselectata.nume_categorie}'. Vă rugăm resetați filtrele.",
                    code='categorie_modificata'
                )
        return cleaned_data
    
    
    
    
def validate_fara_linkuri(value):
    if re.search(r'https?:\/\/', str(value).lower()):
        raise ValidationError(
            "Acest camp nu poate contine link-uri (http:// sau https://).",
            code='link_interzis'
        )

def validate_incepe_cu_majuscula(value):
    if not str(value)[0].isupper():
        raise ValidationError(
            "Textul trebuie sa inceapa cu litera mare.",
            code='fara_majuscula_initiala'
        )

class FigurinaModelForm(forms.ModelForm):
    
    pret_achizitie = forms.DecimalField(
        label="Pret de Achizitie (RON)",
        required=True,
        decimal_places=2,
        max_digits=10,
        help_text="Pretul de baza al produsului de la furnizor."
    )
    
    procentaj_adaos = forms.IntegerField(
        label="Procentaj Adaos Comercial (%)",
        required=True,
        validators=[MinValueValidator(0)],
        help_text="Procentaj de adaos comercial (ex: 30 pentru 30%)."
    )
    
    stoc_disponibil = forms.IntegerField(
        label="Stoc Disponibil",
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Cantitate...'}),
        help_text="Numarul de bucati disponibile initial."
    )
    
    nume_figurina = forms.CharField(
        label="Numele Figurinei",
        max_length=100,
        validators=[validate_incepe_cu_majuscula, validate_fara_linkuri]
    )

    descriere = forms.CharField(
        label="Descriere Produs",
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        validators=[validate_fara_linkuri]
    )


    class Meta:
        model = Figurina
        
        fields = [
            'nume_figurina',
            'descriere',
            'imagine',
            'greutate',
            'stoc_disponibil',
            'data_lansare',
            'tara_origine',
            'stare',
            'id_categorie',
            'id_producator',
            'id_serie',
            'materiale',
            'seturi_accesorii',
        ]
        
        exclude = ['stare', 'data_lansare'] 
        
        labels = {
            'stoc_disponibil': 'Cantitate Stoc Initial',
            'nume_figurina': 'Numele Figurinei',
        }
        
        help_texts = {
            'greutate': 'Specificati greutatea in Kilograme (ex: 1.25).',
        }
        
        widgets = {
            'data_lansare': forms.DateInput(attrs={'type': 'date'}),
            'materiale': forms.CheckboxSelectMultiple,
            'seturi_accesorii': forms.CheckboxSelectMultiple,
        }

    
    def clean_procentaj_adaos(self):
        adaos = self.cleaned_data.get('procentaj_adaos')
        if adaos is not None and adaos < 0:
            raise ValidationError(
                "Procentajul de adaos nu poate fi un numar negativ.",
                code='adaos_negativ'
            )
        return adaos

    
    def clean(self):
        cleaned_data = super().clean()
        stoc = cleaned_data.get('stoc_disponibil')
        pret_achizitie = cleaned_data.get('pret_achizitie')

        if stoc is not None and pret_achizitie is not None:
            if stoc == 0 and pret_achizitie > 0:
                raise ValidationError(
                    "Eroare: Nu puteti seta un pret de achizitie pentru un produs adaugat cu stoc zero.",
                    code='pret_fara_stoc'
                )
        
        return cleaned_data
    
    
    
    
    
    
def validate_name_format(value):
    if not value[0].isupper():
        raise ValidationError(
            "Textul trebuie sa inceapa cu litera mare.",
            code='nu_incepe_cu_majuscula'
        )
    if not re.match(r'^[A-Za-z -]+$', value):
        raise ValidationError(
            "Textul poate contine doar litere, spatii si cratima.",
            code='caractere_nepermise'
        )

def validate_capitalization_after_separator(value):
    if re.search(r'[ -][a-z]', value):
        raise ValidationError(
            "Dupa spatiu sau cratima trebuie sa urmeze o litera mare.",
            code='litera_mica_dupa_separator'
        )

def validate_no_links(value):
    if re.search(r'https?:\/\/', value.lower()):
        raise ValidationError(
            "Campul nu poate contine link-uri (http:// sau https://).",
            code='link_detectat'
        )

def validate_word_count_5_to_100(value):
    words = re.findall(r'\w+', value)
    count = len(words)
    if not (5 <= count <= 100):
        raise ValidationError(
            f"Mesajul trebuie sa contina intre 5 si 100 de cuvinte. (Ati scris {count})",
            code='numar_cuvinte_invalid'
        )

def validate_max_word_length_15(value):
    words = re.findall(r'\w+', value)
    long_words = [word for word in words if len(word) > 15]
    if long_words:
        examples = ", ".join(long_words[:3])
        raise ValidationError(
            f"Urmatoarele cuvinte sunt prea lungi (max 15 caractere): {examples}...",
            code='cuvant_prea_lung'
        )

def validate_is_major(value_date):
    today = datetime.date.today()
    eighteen_years_ago = today.replace(year=today.year - 18)
    
    if value_date > eighteen_years_ago:
        raise ValidationError(
            "Trebuie sa fiti major (18 ani impliniti) pentru a trimite un mesaj.",
            code='minor'
        )

def validate_not_temp_email(value):
    try:
        domain = value.split('@')[-1].lower()
        if domain in ['guerillamail.com', 'yopmail.com']:
            raise ValidationError(
                "Acest domeniu de e-mail temporar nu este permis. Va rugam folositi o adresa de e-mail valida.",
                code='email_temporar'
            )
    except (IndexError, AttributeError):
        pass

class ContactForm(forms.Form):
    TIP_MESAJ_CHOICES = [
        ('neselectat', '--- Neselectat ---'),
        ('reclamatie', 'Reclamatie'),
        ('intrebare', 'Intrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]

    nume = forms.CharField(
        label="Nume",
        max_length=10,
        required=True,
        validators=[validate_name_format, validate_capitalization_after_separator]
    )
    
    prenume = forms.CharField(
        label="Prenume",
        max_length=10,
        required=False
    )
    
    cnp = forms.CharField(
        label="CNP",
        min_length=13,
        max_length=13,
        required=False,
        help_text="Optional. Trebuie sa contina exact 13 cifre."
    )
    
    data_nasterii = forms.DateField(
        label="Data Nasterii",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[validate_is_major]
    )
    
    email = forms.EmailField(
        label="E-mail",
        required=True,
        validators=[validate_not_temp_email]
    )
    
    confirmare_email = forms.EmailField(
        label="Confirmare E-mail",
        required=True
    )
    
    tip_mesaj = forms.ChoiceField(
        label="Tipul Mesajului",
        choices=TIP_MESAJ_CHOICES,
        required=True,
        initial='neselectat',
        widget=forms.Select
    )
    
    subiect = forms.CharField(
        label="Subiect",
        max_length=100,
        required=True,
        validators=[validate_name_format, validate_no_links]
    )
    
    zile_asteptare_help_text = (
        "Pentru review-uri/cereri minimul de zile de asteptare trebuie setat de la 4 incolo "
        "iar pentru cereri/intrebari de la 2 incolo. Maximul e 30."
    )
    minim_zile_asteptare = forms.IntegerField(
        label="Minim zile asteptare",
        required=True,
        help_text=zile_asteptare_help_text,
        validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    
    mesaj = forms.CharField(
        label="Mesajul dumneavoastra (va rugam sa va si semnati)",
        required=True,
        widget=forms.Textarea(attrs={'rows': 6}),
        validators=[
            validate_word_count_5_to_100,
            validate_max_word_length_15,
            validate_no_links
        ]
    )


    def clean_prenume(self):
        prenume = self.cleaned_data.get('prenume')
        if prenume:
            try:
                validate_name_format(prenume)
                validate_capitalization_after_separator(prenume)
            except ValidationError as e:
                self.add_error('prenume', e)
        return prenume

    def clean_cnp(self):
        cnp = self.cleaned_data.get('cnp')
        if not cnp:
            return cnp
            
        if not cnp.isdigit() or len(cnp) != 13:
            raise ValidationError("CNP-ul trebuie sa contina exact 13 cifre.", code='cnp_invalid_format')
        
        if cnp[0] not in ('1', '2'):
            raise ValidationError("CNP-ul trebuie sa inceapa cu cifra 1 sau 2.", code='cnp_s_invalid')
        
        try:
            an = int("19" + cnp[1:3])
            luna = int(cnp[3:5])
            zi = int(cnp[5:7])
            datetime.date(an, luna, zi)
        except ValueError:
            raise ValidationError("Data din CNP (cifrele 2-7) nu este o data valida.", code='cnp_data_invalida')
        
        return cnp

    def clean_tip_mesaj(self):
        tip = self.cleaned_data.get('tip_mesaj')
        if tip == 'neselectat':
            raise ValidationError("Va rugam sa selectati un tip de mesaj valid.", code='tip_neselectat')
        return tip


    def clean(self):
        cleaned_data = super().clean()
        
        email = cleaned_data.get('email')
        confirmare_email = cleaned_data.get('confirmare_email')
        nume = cleaned_data.get('nume')
        mesaj = cleaned_data.get('mesaj')
        tip_mesaj = cleaned_data.get('tip_mesaj')
        zile_asteptare = cleaned_data.get('minim_zile_asteptare')
        cnp = cleaned_data.get('cnp')
        data_nasterii = cleaned_data.get('data_nasterii')

        if email and confirmare_email and email != confirmare_email:
            self.add_error('confirmare_email', "Adresele de e-mail nu se potrivesc.")

        if tip_mesaj and zile_asteptare is not None:
            if tip_mesaj in ('review', 'cerere') and zile_asteptare < 4:
                self.add_error('minim_zile_asteptare', 
                                "Pentru Review-uri/Cereri, minimul de zile de asteptare este 4.")
            
            elif tip_mesaj == 'intrebare' and zile_asteptare < 2:
                self.add_error('minim_zile_asteptare', 
                                "Pentru Intrebari, minimul de zile de asteptare este 2.")
        if nume and mesaj:
            if 'nume' not in self.errors and 'mesaj' not in self.errors:
                words = re.findall(r'\w+', mesaj)
                if not words or words[-1] != nume:
                    self.add_error('mesaj', 
                                    f"Mesajul trebuie sa se incheie cu numele dumneavoastra ('{nume}') ca semnatura.")
        
        if cnp and data_nasterii:
            if 'cnp' not in self.errors and 'data_nasterii' not in self.errors:
                cnp_an = cnp[1:3]
                form_an = data_nasterii.strftime('%y')
                
                cnp_luna = cnp[3:5]
                form_luna = data_nasterii.strftime('%m')
                
                cnp_zi = cnp[5:7]
                form_zi = data_nasterii.strftime('%d')
                
                if cnp_an != form_an or cnp_luna != form_luna or cnp_zi != form_zi:
                    self.add_error('cnp', 
                        f"Data nasterii ({data_nasterii.strftime('%d.%m.%Y')}) "
                        f"nu corespunde cu data din CNP ({cnp_zi}.{cnp_luna}.19{cnp_an})."
                    )

        return cleaned_data
    
    
class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                    'telefon', 'data_nasterii', 'adresa_strada', 
                    'adresa_oras', 'adresa_judet', 'adresa_cod_postal')
        
        widgets = {
            'data_nasterii': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if data_nasterii:
            today = datetime.date.today()
            fourteen_years_ago = today.replace(year=today.year - 14)
            if data_nasterii > fourteen_years_ago:
                raise ValidationError("Trebuie sa aveti cel putin 14 ani pentru a va inregistra.", code='varsta_prea_mica')
        return data_nasterii

    def clean_adresa_cod_postal(self):
        cod_postal = self.cleaned_data.get('adresa_cod_postal')
        if cod_postal and not cod_postal.isdigit():
            raise ValidationError("Codul postal trebuie sa contina doar cifre.", code='cod_postal_invalid')
        return cod_postal

    def clean_adresa_oras(self):
        oras = self.cleaned_data.get('adresa_oras')
        if oras and oras.lower() == 'nespecificat':
            raise ValidationError("Va rugam sa introduceti un oras valid.", code='oras_nespecificat')
        return oras
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.lower() == 'admin':
            logger.critical("CRITICAL: Tentativa de inregistrare cu username interzis 'ADMIN'!")
            email_incercare = self.data.get('email', 'Nespecificat')
            subiect = "cineva incearca sa ne preia site-ul"
            mesaj_text = f"Tentativa de inregistrare cu user 'admin'. Email folosit: {email_incercare}"
            mesaj_html = f"""
                <h1 style="color: red;">{subiect}</h1>
                <p>{mesaj_text}</p>
            """
            mail_admins(
                subject=subiect,
                message=mesaj_text,
                html_message=mesaj_html,
                fail_silently=True
            )
            
            raise ValidationError("Acest nume de utilizator nu este permis.", code='forbidden_username')
            
        return username
    

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        label="Tine-ma minte (o zi)",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    
class FigurinaModelForm(forms.ModelForm):
    class Meta:
        model = Figurina
        
        fields = '__all__'
        
        widgets = {
            'data_lansare': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d' 
            ),
            'descriere': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Introduceți o descriere detaliată...'}
            ),
            'materiale': forms.CheckboxSelectMultiple,
            'seturi_accesorii': forms.CheckboxSelectMultiple,
            
            'id_categorie': forms.Select,
            'id_producator': forms.Select,
            'id_serie': forms.Select,
        }
        
        labels = {
            'nume_figurina': 'Numele Figurinei',
            'id_categorie': 'Categorie',
            'id_producator': 'Producator',
            'id_serie': 'Serie',
            'stoc_disponibil': 'Stoc',
            'tara_origine': 'Tara de Origine',
        }
        
class PromotieForm(forms.ModelForm):
    categorii = forms.ModelMultipleChoiceField(
        queryset=Categorie.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecteazs categoriile (Doar cele cu template existent!)"
    )
    valabilitate_zile = forms.IntegerField(min_value=1, initial=7, label="Valabilitate (zile)")
    class Meta:
        model = Promotie
        fields = ['nume', 'subiect', 'mesaj', 'categorii']
        widgets = {
            'mesaj': forms.Textarea(attrs={'rows': 4}),
        }