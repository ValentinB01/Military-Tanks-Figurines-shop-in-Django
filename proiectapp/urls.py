from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('despre/', views.despre, name='despre'),
    path('produse/', views.produse, name='produse'),
    path('contact/', views.contact, name='contact'),
    path('cos_virtual/', views.cos_virtual, name='cos_virtual'),    
    path('log/', views.log_view, name='log'),
    path('info/', views.info_view, name='info'),
    path('produse/<int:id_figurina>/', views.produs_detaliu, name='produs_detaliu'),
    path('categorii/<str:nume_categorie>/', views.categorie_detaliu, name='categorie_detaliu'),
    path('serii/', views.serie_list, name='serie_list'),
    path('serii/<int:id_serie>/', views.serie_detaliu, name='serie_detaliu'),
    path('shipping-returns/', views.in_lucru, name='shipping_returns'),
    path('privacy-policy/', views.in_lucru, name='privacy_policy'),
    path('terms-conditions/', views.in_lucru, name='terms_conditions'),
    path('produse/adauga/', views.adauga_produs, name='adauga_produs'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('schimba-parola/', views.change_password_view, name='change_password'),
    path('confirma_mail/<str:cod>/', views.confirma_mail, name='confirma_mail'),
    path('promotii/', views.promotii_view, name='promotii'),
    path('interzis/', views.view_403, name='interzis'),
    path('accesare-oferta/', views.accesare_oferta, name='accesare_oferta'),
    path('oferta/', views.oferta_view, name='oferta'),
]