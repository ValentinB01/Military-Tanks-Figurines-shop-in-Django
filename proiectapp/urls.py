from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('despre/', views.despre, name='despre'),
    path('produse/', views.produse, name='produse'),
    path('contact/', views.contact, name='contact'),
    path('cos_virtual/', views.cos_virtual, name='cos_virtual'),    
    path('log/', views.log_view, name='log'),
    path('info/', views.info_view, name='info'),
]