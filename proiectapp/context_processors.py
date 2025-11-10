from .models import Categorie, Seria

def ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return {'ip_address': ip}

def categorii_meniu(request):
    categorii = Categorie.objects.filter(activa=True)
    return {'categorii_meniu': categorii}

def serii_meniu(request):
    serii = Seria.objects.filter(disponibilitate=True).order_by('nume_serie')
    return {'serii_meniu': serii}