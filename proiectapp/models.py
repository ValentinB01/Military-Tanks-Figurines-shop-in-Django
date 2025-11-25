from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Numarul de telefon trebuie sa fie in formatul: '+999999999'. Pana la 15 cifre permise."
    )
    
    telefon = models.CharField(
        validators=[phone_validator], 
        max_length=17, 
        blank=True, 
        null=True,
        help_text="Numarul de telefon (optional)."
    )
    
    data_nasterii = models.DateField(
        blank=True, 
        null=True,
        help_text="Data nasterii (optional)."
    )
    
    adresa_strada = models.CharField(
        max_length=255, 
        blank=True, 
        null=True
    )
    
    adresa_oras = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    
    adresa_judet = models.CharField(
        max_length=100, 
        blank=True, 
        null=True
    )
    
    adresa_cod_postal = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Codul postal (optional)."
    )
    
    cod = models.CharField(
        max_length = 100,
        blank = True,
        null = True
    )
    
    email_confirmat = models.BooleanField(
        default=False
        )
    
    blocat = models.BooleanField(
        default=False, 
        help_text="Daca este bifat, utilizatorul nu se poate loga pe site."
    )
    
    def __str__(self):
        return self.username

class AccessLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    class Meta:
        verbose_name = "Log Acces"
        verbose_name_plural = "Loguri Acces"
    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"
    def afis_data(self):
        acum = timezone.localtime(self.timestamp)        
        zile_sapt = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
        luni = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
                "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]
        zi_sapt = zile_sapt[acum.weekday()]
        zi_luna = acum.day
        luna = luni[acum.month -1]
        an = acum.year
        ora = acum.strftime("%H:%M:%S")
        return f"{zi_sapt}, {zi_luna} {luna} {an}, ora {ora}"


class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    nume_categorie = models.CharField(max_length=100, unique=True)
    descriere = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    culoare = models.CharField(
        max_length=7, 
        default='#333333', 
        help_text="Culoarea categoriei"
    )
    culoare_activa = models.CharField(
        max_length=7, 
        default='#007BFF',
        help_text="Culoarea pentru hover"
    )
    class Meta:
        verbose_name = "Categorie"
        verbose_name_plural = "Categorii"
    def __str__(self):
        return self.nume_categorie

class Producator(models.Model):
    id_producator = models.AutoField(primary_key=True)
    nume_producator = models.CharField(max_length=100, unique=True)
    tara_origine = models.CharField(max_length=50)
    telefon = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    activ = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Producator"
        verbose_name_plural = "Producatori"
    def __str__(self):
        return self.nume_producator

class Seria(models.Model):
    SCALA_CHOICES = [
        ('1:35', '1:35'),
        ('1:48', '1:48'),
        ('1:72', '1:72'),
        ('1:100', '1:100'),
        ('1:144', '1:144'),
    ]
    id_serie = models.AutoField(primary_key=True)
    nume_serie = models.CharField(max_length=100)
    an_lansare = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2025)]
    )
    descriere = models.TextField(blank=True, null=True)
    disponibilitate = models.BooleanField(default=True)
    scala = models.CharField(
        max_length=10, 
        choices=SCALA_CHOICES,
        default='1:35'
    )
    id_producator = models.ForeignKey(Producator, on_delete=models.CASCADE)
    imagine_serie = models.ImageField(
        upload_to='serii_imagini/',
        null=True,
        blank=True,
        verbose_name="Imagine Serie"
    )
    class Meta:
        verbose_name = "Serie"
        verbose_name_plural = "Serii"
    def __str__(self):
        return f"{self.nume_serie} ({self.scala})"

class SetAccessorii(models.Model):
    TIP_ACCESORII_CHOICES = [
        ('CAM', 'Camuflaj'),
        ('UNEL', 'Unelte'),
        ('VOP', 'Vopsele'),
        ('LANT', 'Lanturi'),
        ('ALT', 'Altele'),
    ]
    id_set = models.AutoField(primary_key=True)
    nume_set = models.CharField(max_length=100, unique=True)
    nr_piese = models.IntegerField(default=1)
    compatibilitate = models.CharField(max_length=200)
    editie_speciala = models.BooleanField(default=False)
    tip_accesorii = models.CharField(
        max_length=4, 
        choices=TIP_ACCESORII_CHOICES,
        default='CAM' 
    )
    data_creare = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Set Accesorii"
        verbose_name_plural = "Seturi Accesorii"
    def __str__(self):
        return self.nume_set

class Material(models.Model):
    TEXTURA_CHOICES = [
        ('NETE', 'Neteda'),
        ('MAT', 'Mata'),
        ('STR', 'Stralucitoare'),
        ('TEXT', 'Texturată'),
    ]
    id_material = models.AutoField(primary_key=True)
    tip_material = models.CharField(max_length=100, unique=True)
    culoare = models.CharField(max_length=50, blank=True, null=True)
    rezistent_la_apa = models.BooleanField(default=False)
    textura = models.CharField(
        max_length=4, 
        choices=TEXTURA_CHOICES,
        default='NETE'
    )
    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiale"
    def __str__(self):
        return f"{self.tip_material}"

class Figurina(models.Model):
    STARE_CHOICES = [
        ('NOU', 'Nou'),
        ('FOL', 'Folosit'),
        ('COL', 'Colectie'),
        ('RES', 'Restaurat'),
    ]
    TARA_ORIGINE_CHOICES = [
        ('USA', 'Statele Unite'),
        ('GER', 'Germania'),
        ('RUS', 'Rusia'),
        ('UK', 'Marea Britanie'),
        ('JAP', 'Japonia'),
        ('SU', 'Suedia'),
        ('CHN', 'China'),
        ('FRA', 'Franta'),
        ('ITA', 'Italia')
    ]
    id_figurina = models.AutoField(primary_key=True)
    nume_figurina = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    greutate = models.DecimalField(max_digits=6, decimal_places=2, help_text="Greutate in kg")
    stoc_disponibil = models.IntegerField(default=0)
    data_lansare = models.DateField()
    data_adaugare = models.DateTimeField(auto_now_add=True)
    tara_origine = models.CharField(
        max_length=3,
        choices=TARA_ORIGINE_CHOICES,
        default='None'
    )
    stare = models.CharField(
        max_length=3,
        choices=STARE_CHOICES,
        default='NOU'
    )
    descriere = models.TextField(blank=True, null=True)
    imagine = models.ImageField(
        upload_to='produse_imagini/',
        null=True,
        blank=True
    )
    id_categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    id_producator = models.ForeignKey(Producator, on_delete=models.CASCADE)
    id_serie = models.ForeignKey(Seria, on_delete=models.CASCADE)
    materiale = models.ManyToManyField(Material, through='FigurinaMaterial')
    seturi_accesorii = models.ManyToManyField(SetAccessorii, through='FigurinaSetAccesorii')
    class Meta:
        verbose_name = "Figurina"
        verbose_name_plural = "Figurine"
    def __str__(self):
        return self.nume_figurina

class FigurinaMaterial(models.Model):
    figurina = models.ForeignKey(Figurina, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    procentaj = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100.00,
        help_text="Procentajul materialului în figurina"
    )
    class Meta:
        unique_together = ['figurina', 'material']

class FigurinaSetAccesorii(models.Model):
    figurina = models.ForeignKey(Figurina, on_delete=models.CASCADE)
    set_accesorii = models.ForeignKey(SetAccessorii, on_delete=models.CASCADE)
    data_asociere = models.DateTimeField(auto_now_add=True)
    compatibil_perfect = models.BooleanField(default=True)
    class Meta:
        unique_together = ['figurina', 'set_accesorii']
        
        


class Vizualizare(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    produs = models.ForeignKey(Figurina, on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.produs.nume_figurina}"

class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateTimeField()
    
    subiect = models.CharField(max_length=255)
    mesaj = models.TextField()
    
    categorii = models.ManyToManyField(Categorie)

    def __str__(self):
        return self.nume