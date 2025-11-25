from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, AccessLog, Categorie, Producator, 
    Seria, SetAccessorii, Material, Figurina, 
    FigurinaMaterial, FigurinaSetAccesorii
)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Date Suplimentare', {
            'fields': (
                'telefon', 
                'data_nasterii', 
                'adresa_strada', 
                'adresa_oras', 
                'adresa_judet', 
                'adresa_cod_postal',
                'cod',
                'email_confirmat',
                'blocat'
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []

        if request.user.groups.filter(name='Moderatori').exists():
            campuri_editabile = ['first_name', 'last_name', 'email', 'blocat']
            
            toate_campurile = [f.name for f in self.model._meta.fields]
            
            campuri_extra = [
                'password', 'last_login', 'date_joined', 
                'is_superuser', 'is_staff', 'is_active', 
                'groups', 'user_permissions'
            ]
            toate_campurile.extend(campuri_extra)

            return [f for f in toate_campurile if f not in campuri_editabile]

        return super().get_readonly_fields(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AccessLog)
admin.site.register(Categorie)
admin.site.register(Producator)
admin.site.register(Seria)
admin.site.register(SetAccessorii)
admin.site.register(Material)
admin.site.register(Figurina)
admin.site.register(FigurinaMaterial)
admin.site.register(FigurinaSetAccesorii)