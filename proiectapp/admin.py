from django.contrib import admin
from .models import *

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['id_categorie', 'nume_categorie', 'activa']
    list_per_page = 5
    list_filter = ['activa']
    search_fields = ['id_categorie', 'nume_categorie']
    ordering = ['nume_categorie']
    list_editable = ['activa']

@admin.register(Producator)
class ProducatorAdmin(admin.ModelAdmin):
    list_display = ['id_producator', 'nume_producator', 'tara_origine', 'activ', 'email']
    list_filter = ['activ', 'tara_origine']
    search_fields = ['nume_producator', 'tara_origine']
    list_editable = ['activ']

@admin.register(Seria)
class SeriaAdmin(admin.ModelAdmin):
    list_display = ['id_serie', 'nume_serie', 'scala', 'an_lansare', 'disponibilitate', 'id_producator']
    list_filter = ['scala', 'disponibilitate', 'an_lansare', 'id_producator']
    search_fields = ['id_serie', 'nume_serie']
    list_editable = ['disponibilitate']

@admin.register(SetAccessorii)
class SetAccessoriiAdmin(admin.ModelAdmin):
    list_display = ['id_set', 'nume_set', 'tip_accesorii', 'nr_piese', 'editie_speciala', 'data_creare']
    list_filter = ['tip_accesorii', 'editie_speciala']
    search_fields = ['nume_set', 'compatibilitate']
    readonly_fields = ['data_creare']  

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id_material', 'tip_material', 'culoare', 'textura', 'rezistent_la_apa']
    list_filter = ['textura', 'rezistent_la_apa']
    search_fields = ['tip_material', 'culoare']

class FigurinaMaterialInline(admin.TabularInline):
    model = FigurinaMaterial
    extra = 1 
    verbose_name = "Material"
    verbose_name_plural = "Materiale utilizate"

class FigurinaSetAccesoriiInline(admin.TabularInline):
    model = FigurinaSetAccesorii
    extra = 1
    verbose_name = "Set accesorii compatibil"
    verbose_name_plural = "Seturi accesorii compatibile"

@admin.register(Figurina)
class FigurinaAdmin(admin.ModelAdmin):
    list_display = [
        'id_figurina', 
        'nume_figurina', 
        'pret', 
        'stoc_disponibil', 
        'tara_origine', 
        'stare',
        'id_categorie',
        'data_adaugare'
    ]
    list_per_page = 5
    list_filter = [
        'tara_origine',
        'stare', 
        'id_categorie',
        'id_producator',
        'data_lansare'
    ]
    search_fields = [
        'nume_figurina',
        'descriere'
    ]
    ordering = ['-data_adaugare']
    list_editable = [
        'pret',
        'stoc_disponibil'
    ]
    readonly_fields = [
        'data_adaugare'
    ]
    list_select_related = ['id_categorie', 'id_producator', 'id_serie']
    inlines = [FigurinaMaterialInline, FigurinaSetAccesoriiInline]
    fieldsets = (
        ('Informatii de baza', {
            'fields': (
                'nume_figurina',
                'imagine', 
                'pret', 
                'greutate', 
                'stoc_disponibil',
                'data_lansare',
                'data_adaugare'
            )
        }),
        ('Categorizare', {
            'fields': (
                'tara_origine',
                'stare',
                'id_categorie',
                'id_producator', 
                'id_serie'
            )
        }),
        ('Descriere', {
            'fields': ('descriere',),
            'classes': ('collapse',)  
        }),
    )