from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Categorie, Producator, Figurina, Seria, AccessLog, CustomUser, Vizualizare # Asigură-te că ai și CustomUser
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from collections import OrderedDict
from django.conf import settings
import datetime
from django.core.paginator import Paginator
import re
import json
import os
import time
from django.conf import settings
import uuid
import logging
from django.core.mail import send_mail
from django.urls import reverse
from django.core.mail import mail_admins
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.core.mail import send_mass_mail
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


from .forms import (
    FigurinaFiltruForm, 
    ContactForm, 
    FigurinaModelForm,
    CustomUserCreationForm,
    CustomLoginForm,
    PromotieForm
)


def log_view(request):
    
    is_admin_site = request.user.groups.filter(name='Administratori_site').exists()
    
    if not (request.user.is_superuser or is_admin_site):
        return return_403_custom(request, "Acces Interzis", "Doar administratorii site-ului pot vedea logurile.")
    
    all_logs = AccessLog.objects.all().order_by('-timestamp')
    total_logs = all_logs.count()

    n = request.GET.get('ultimele')
    if n:
        try:
            n = int(n)
            if n <= 0:
                raise ValueError("Numarul trebuie sa fie pozitiv")
            if n > total_logs:
                logs = all_logs
                error_message = f"Exista doar {total_logs} accesari fata de {n} accesari cerute"
            else:
                logs = all_logs[:n]
                error_message = None
                
        except ValueError:
            logs = all_logs
            error_message = 'Parametrul "ultimele" trebuie sa fie un numar intreg pozitiv'
    else:
        logs = all_logs
        error_message = None
        
    accesari_param = request.GET.get('accesari')
    show_access_count = accesari_param == 'nr'
    show_access_details = accesari_param == 'detalii'
    
    ids_from_params = request.GET.getlist('iduri')
    allow_duplicates = request.GET.get('dubluri', 'false').lower() == 'true'
    
    logs_by_id = None
    if ids_from_params:
        all_ids = []
        for id_string in ids_from_params:
            try:
                ids = [int(id_str.strip()) for id_str in id_string.split(',')]
                all_ids.extend(ids)
            except ValueError:
                continue
        
        if not allow_duplicates:
            unique_ids = list(OrderedDict.fromkeys(all_ids))
            all_ids = unique_ids
        
        if all_ids:
            logs_by_id = AccessLog.objects.filter(id__in=all_ids)
            log_dict = {log.id: log for log in logs_by_id}
            logs_by_id = [log_dict[log_id] for log_id in all_ids if log_id in log_dict]
            
    tabel_param = request.GET.get('tabel')
    show_table = False
    table_columns = []
    all_valid_model_columns = ['id', 'timestamp', 'method', 'path', 'ip_address']
    if tabel_param:
        show_table = True
        if tabel_param == 'tot':
            table_columns = all_valid_model_columns
        else:
            valid_columns_map = {
                'id': 'id',
                'timestamp': 'timestamp',
                'method': 'method',
                'path': 'path',
                'url': 'path',
                'ip_address': 'ip_address'
            }
            requested_columns = [col.strip() for col in tabel_param.split(',')]
            temp_cols = []
            for col_name in requested_columns:
                real_col_name = valid_columns_map.get(col_name)
                if real_col_name:
                    temp_cols.append(real_col_name)
            
            table_columns = list(OrderedDict.fromkeys(temp_cols))
            
            if not table_columns:
                table_columns = all_valid_model_columns
                
    table_data = logs_by_id if logs_by_id else logs
    
    
    
    page_stats = AccessLog.objects.values('path').annotate(
        access_count=Count('id')
    ).order_by('access_count')
    if page_stats:
        least_accessed = page_stats.first()
        most_accessed = page_stats.last()
    else:
        least_accessed = None
        most_accessed = None
    
    context = {
        'logs': logs,
        'error_message': error_message,
        'total_logs': total_logs,
        'show_access_count': show_access_count,
        'show_access_details': show_access_details,
        'logs_by_id': logs_by_id,
        'allow_duplicates': allow_duplicates,
        'show_table': show_table,
        'table_columns': table_columns,
        'table_data': table_data,
        'least_accessed': least_accessed,
        'most_accessed': most_accessed,
        'current_params': request.GET,
    }
    return render(request, 'log.html', context)


def info_view(request):
    params = request.GET
    param_count = len(params)
    param_names = list(params.keys())
    param_details = []
    for name, values in params.lists():
        param_details.append({
            'name': name,
            'values': values,
            'count': len(values)
        })
    
    context = {
        'param_count': param_count,
        'param_names': param_names,
        'param_details': param_details,
    }
    return render(request, 'info.html', context)


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

logger = logging.getLogger('proiectapp')

def index(request):
    if request.GET:
        logger.debug(f"DEBUG: Filtrare produse cu parametrii: {request.GET.dict()}")
    
    featured_series = Seria.objects.filter(
        disponibilitate=True,
        imagine_serie__isnull=False
    ).order_by('?')[:3]

    context = {
        'ip_address': get_ip_address(request),
        'featured_series': featured_series
    }
        
    return render(request, 'index.html', context)

def despre(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'despre.html', context)

def in_lucru(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'in_lucru.html', context)

def cos_virtual(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'in_lucru.html', context)

def produse(request):
    if request.GET:
        logger.debug(f"DEBUG: Filtrare produse cu parametrii: {request.GET.dict()}")
    
    figurine_list = Figurina.objects.select_related(
        'id_categorie', 'id_producator', 'id_serie'
    ).prefetch_related('materiale', 'seturi_accesorii').all()

    params_get = request.GET.copy()
    form = FigurinaFiltruForm(request.GET)

    elemente_pe_pagina = 5
    repaginare_warning = False
    page_number_str = request.GET.get('page')
    if page_number_str and not page_number_str.isdigit():
        logger.warning(f"WARNING: Parametru de paginare invalid primit: {page_number_str}")

    if request.GET:
        if form.is_valid():
            nume_query = request.GET.get('nume_figurina')
            if nume_query:
                figurine_list = figurine_list.filter(nume_figurina__icontains=nume_query)
            
            pret_min_query = request.GET.get('pret_min')
            if pret_min_query:
                figurine_list = figurine_list.filter(pret__gte=pret_min_query)
            
            pret_max_query = request.GET.get('pret_max')
            if pret_max_query:
                figurine_list = figurine_list.filter(pret__lte=pret_max_query)
            
            greutate_min_query = request.GET.get('greutate_min')
            if greutate_min_query:
                figurine_list = figurine_list.filter(greutate__gte=greutate_min_query)  
            
            greutate_max_query = request.GET.get('greutate_max')
            if greutate_max_query:
                figurine_list = figurine_list.filter(greutate__lte=greutate_max_query)
            
            data_min_query = request.GET.get('data_lansare_min')
            if data_min_query:
                figurine_list = figurine_list.filter(data_lansare__gte=data_min_query)
                
            data_max_query = request.GET.get('data_lansare_max')
            if data_max_query:
                figurine_list = figurine_list.filter(data_lansare__lte=data_max_query)
            
            stare_query = request.GET.getlist('stare')
            if stare_query:
                figurine_list = figurine_list.filter(stare__in=stare_query)
                
            tara_query = request.GET.getlist('tara_origine')
            if tara_query:
                figurine_list = figurine_list.filter(tara_origine__in=tara_query)
                
            categorie_query = request.GET.getlist('id_categorie')
            if categorie_query:
                figurine_list = figurine_list.filter(id_categorie__in=categorie_query)
                
            producator_query = request.GET.getlist('id_producator')
            if producator_query:
                figurine_list = figurine_list.filter(id_producator__in=producator_query)
                
            serie_query = request.GET.getlist('id_serie')
            if serie_query:
                figurine_list = figurine_list.filter(id_serie__in=serie_query)
                
            materiale_query = request.GET.getlist('materiale')
            if materiale_query:
                figurine_list = figurine_list.filter(materiale__in=materiale_query).distinct() 
            
            per_pagina_val = form.cleaned_data.get('per_pagina')
            if per_pagina_val:
                try:
                    elemente_pe_pagina = int(per_pagina_val)
                    
                    if page_number_str and int(page_number_str) > 1:
                        repaginare_warning = True
                except (ValueError, TypeError):
                    elemente_pe_pagina = 5 
                    
            sort_by = request.GET.get('ordonare')
            
            sort_by_link = None 

            if not sort_by:
                sort_by_link = request.GET.get('sort')
            
            if sort_by_link == 'a':
                sort_by = 'pret'
            elif sort_by_link == 'd':
                sort_by = '-pret'
            elif not sort_by: 
                sort_by = 'nume_figurina'
        else:
            figurine_list = Figurina.objects.none()
            per_pagina_val_fallback = request.GET.get('per_pagina')
            if per_pagina_val_fallback:
                try:
                    elemente_pe_pagina = int(per_pagina_val_fallback)
                except (ValueError, TypeError):
                    pass
    
    else:
        figurine_list = figurine_list.order_by('nume_figurina')


    paginator = Paginator(figurine_list, elemente_pe_pagina)
    page_obj = paginator.get_page(page_number_str)
    
    params_for_pagination = params_get.copy()
    if 'page' in params_for_pagination:
        del params_for_pagination['page']
    
    params_for_sorting = params_get.copy()
    if 'sort' in params_for_sorting:
        del params_for_sorting['sort']

    context = {
        'page_obj': page_obj,
        'params_pagination': params_for_pagination.urlencode(),
        'params_sorting': params_for_sorting.urlencode(),
        'ip_address': get_ip_address(request),
        'form': form,
        'repaginare_warning': repaginare_warning
    }
    return render(request, 'produse.html', context)


def produs_detaliu(request, id_figurina):
    figurina = get_object_or_404(Figurina, id_figurina=id_figurina)
    
    if figurina.stoc_disponibil < 3:
        logger.warning(f"WARNING: Stoc critic pentru produsul {figurina.nume_figurina} (ID: {id_figurina})")
    
    if request.user.is_authenticated:
        Vizualizare.objects.create(
            user=request.user,
            produs=figurina
        )
        
        N = 5
        vizualizari_user = Vizualizare.objects.filter(user=request.user).order_by('data_vizualizare')
        
        if vizualizari_user.count() > N:
            vizualizari_user.first().delete()
    context = {
        'fig': figurina,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'produs_detaliu.html', context)


def categorie_detaliu(request, nume_categorie):
    categorie = get_object_or_404(Categorie, nume_categorie=nume_categorie)
    figurine_list = Figurina.objects.filter(id_categorie=categorie).select_related(
        'id_categorie', 'id_producator', 'id_serie'
    ).prefetch_related('materiale')
    
    params_get = request.GET.copy()
    
    form = FigurinaFiltruForm(request.GET, categorie_preselectata=categorie)
    
    elemente_pe_pagina = 5
    repaginare_warning = False
    page_number_str = request.GET.get('page')

    if request.GET:
        if form.is_valid():
            
            nume_query = form.cleaned_data.get('nume_figurina')
            if nume_query:
                figurine_list = figurine_list.filter(nume_figurina__icontains=nume_query)
            pret_min_query = form.cleaned_data.get('pret_min')
            if pret_min_query is not None:
                figurine_list = figurine_list.filter(pret__gte=pret_min_query)
            pret_max_query = form.cleaned_data.get('pret_max')
            if pret_max_query is not None:
                figurine_list = figurine_list.filter(pret__lte=pret_max_query)
            greutate_min_query = form.cleaned_data.get('greutate_min')
            if greutate_min_query is not None:
                figurine_list = figurine_list.filter(greutate__gte=greutate_min_query)  
            greutate_max_query = form.cleaned_data.get('greutate_max')
            if greutate_max_query is not None:
                figurine_list = figurine_list.filter(greutate__lte=greutate_max_query)
            data_min_query = form.cleaned_data.get('data_lansare_min')
            if data_min_query:
                figurine_list = figurine_list.filter(data_lansare__gte=data_min_query)
            data_max_query = form.cleaned_data.get('data_lansare_max')
            if data_max_query:
                figurine_list = figurine_list.filter(data_lansare__lte=data_max_query)
            categorie_query = form.cleaned_data.get('id_categorie')
            if categorie_query:
                figurine_list = figurine_list.filter(id_categorie__in=categorie_query)
            stare_query = form.cleaned_data.get('stare')
            if stare_query:
                figurine_list = figurine_list.filter(stare__in=stare_query)
            
            tara_query = form.cleaned_data.get('tara_origine')
            if tara_query:
                figurine_list = figurine_list.filter(tara_origine__in=tara_query)
            
            producator_query = form.cleaned_data.get('id_producator')
            if producator_query:
                figurine_list = figurine_list.filter(id_producator__in=producator_query)
            
            serie_query = form.cleaned_data.get('id_serie')
            if serie_query:
                figurine_list = figurine_list.filter(id_serie__in=serie_query)
            
            materiale_query = form.cleaned_data.get('materiale')
            if materiale_query:
                figurine_list = figurine_list.filter(materiale__in=materiale_query).distinct() 

            per_pagina_val = form.cleaned_data.get('per_pagina')
            if per_pagina_val:
                try:
                    elemente_pe_pagina = int(per_pagina_val)
                    if page_number_str and int(page_number_str) > 1:
                        repaginare_warning = True
                except (ValueError, TypeError):
                    elemente_pe_pagina = 5
            
            sort_by = request.GET.get('ordonare')
            
            sort_by_link = None 

            if not sort_by:
                sort_by_link = request.GET.get('sort')
            
            if sort_by_link == 'a':
                sort_by = 'pret'
            elif sort_by_link == 'd':
                sort_by = '-pret'
            elif not sort_by: 
                sort_by = 'nume_figurina'
            
            figurine_list = figurine_list.order_by(sort_by)

        else:
            figurine_list = Figurina.objects.none()
            per_pagina_val_fallback = request.GET.get('per_pagina')
            if per_pagina_val_fallback:
                try:
                    elemente_pe_pagina = int(per_pagina_val_fallback)
                except (ValueError, TypeError): pass
    
    else:
        figurine_list = figurine_list.order_by('nume_figurina')
    
    paginator = Paginator(figurine_list, elemente_pe_pagina)
    page_obj = paginator.get_page(page_number_str)
    
    params_for_pagination = params_get.copy()
    if 'page' in params_for_pagination:
        del params_for_pagination['page']
    
    params_for_sorting = params_get.copy()
    if 'sort' in params_for_sorting:
        del params_for_sorting['sort']

    context = {
        'cat': categorie,
        'page_obj': page_obj,
        'form': form,
        'params_pagination': params_for_pagination.urlencode(),
        'params_sorting': params_for_sorting.urlencode(),
        'ip_address': get_ip_address(request),
        'repaginare_warning': repaginare_warning
    }
    return render(request, 'categorie_detaliu.html', context)



def adauga_produs(request):
    if not request.user.has_perm('proiectapp.add_figurina'):
        cnt = request.session.get('cnt_403', 0) + 1
        request.session['cnt_403'] = cnt
        
        context = {
            'titlu': 'Eroare adaugare produse',
            'mesaj_personalizat': 'Nu ai voie să adaugi figurine.',
            'count': cnt,
            'n_max': getattr(settings, 'N_MAX_403', 5)
        }
        return render(request, '403.html', context, status=403)

    if request.method == 'POST':
        form = FigurinaModelForm(request.POST, request.FILES)
        if form.is_valid():
            figurina = form.save(commit=False)
            pret_ach = form.cleaned_data['pret_achizitie']
            adaos = form.cleaned_data['procentaj_adaos']
            figurina.pret = pret_ach * (1 + (adaos / 100))
            figurina.save()
            form.save_m2m()
            messages.success(request, f"Produsul '{figurina.nume_figurina}' a fost adăugat cu succes!")
            return redirect('produse') 
    else:
        form = FigurinaModelForm()

    context = {
        'form': form,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'adauga_produs.html', context)



def serie_list(request):
    serii_list = Seria.objects.filter(disponibilitate=True).order_by('nume_serie')
    
    paginator = Paginator(serii_list, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'serie_list.html', context)

def serie_detaliu(request, id_serie):
    serie = get_object_or_404(Seria, id_serie=id_serie)
    produse_in_serie = Figurina.objects.filter(id_serie=serie)
    context = {
        'serie': serie,
        'produse': produse_in_serie,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'serie_detaliu.html', context)


def _capitalize_sentence_starts(text):
    def capitalize_match(match):
        return match.group(1) + match.group(2) + match.group(3).upper()

    pattern_ellipsis = r'(\.\.\.)(\s*)(\w)'
    text = re.sub(pattern_ellipsis, capitalize_match, text)
    
    pattern_single = r'([.?!])(\s*)(\w)'
    text = re.sub(pattern_single, capitalize_match, text)
    return text

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            logger.info(f"INFO: Mesaj nou de contact primit de la {form.cleaned_data['email']}")
            cd = form.cleaned_data
            today = datetime.date.today()
            data_nasterii = cd.get('data_nasterii')
            varsta_ani = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            varsta_luni = (today.month - data_nasterii.month - (today.day < data_nasterii.day)) % 12
            
            cd['varsta_calculata'] = f"{varsta_ani} ani și {varsta_luni} luni"

            mesaj_original = cd.get('mesaj')
            mesaj_procesat = mesaj_original.replace('\n', ' ')
            mesaj_procesat = re.sub(r'\s+', ' ', mesaj_procesat).strip()
            mesaj_procesat = _capitalize_sentence_starts(mesaj_procesat)
            cd['mesaj_procesat'] = mesaj_procesat
            
            tip_mesaj = cd.get('tip_mesaj')
            zile_asteptare = cd.get('minim_zile_asteptare')
            is_urgent = False
            
            if tip_mesaj in ('review', 'cerere') and zile_asteptare == 4:
                is_urgent = True
            elif tip_mesaj == 'intrebare' and zile_asteptare == 2:
                is_urgent = True
            elif tip_mesaj in ('reclamatie', 'programare') and zile_asteptare == 0:
                is_urgent = True
                
            cd['urgent'] = is_urgent
            
            data_to_save = cd.copy()
            
            data_to_save.pop('confirmare_email', None)
            
            data_to_save['ip_address'] = get_ip_address(request)
            data_to_save['timestamp_sosire'] = datetime.datetime.now().isoformat()
            
            if 'data_nasterii' in data_to_save and isinstance(data_to_save['data_nasterii'], datetime.date):
                data_to_save['data_nasterii'] = data_to_save['data_nasterii'].isoformat()

            timestamp = int(time.time())
            file_name = f"mesaj_{timestamp}"
            if cd.get('urgent'):
                file_name += "_urgent"
            file_name += ".json"

            MESAJE_DIR = os.path.join(settings.BASE_DIR, 'proiectapp', 'Mesaje')
            file_path = os.path.join(MESAJE_DIR, file_name)

            try:
                os.makedirs(MESAJE_DIR, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=4)
                
                messages.success(request, 'Mesajul a fost trimis!')
                return redirect('contact')

            except Exception as e:
                logger.error(f"ERROR: Eroare la salvarea mesajului JSON: {str(e)}")
                subiect = "Eroare la salvare mesaj contact"
                mesaj_text = f"Eroare: {str(e)}"
                
                mesaj_html = f"""
                    <h1 style="color: red;">{subiect}</h1>
                    <p>A apărut o excepție la salvarea fișierului JSON:</p>
                    <div style="background-color: red; color: white; padding: 10px;">
                        {str(e)}
                    </div>
                """
                
                mail_admins(
                    subject=subiect,
                    message=mesaj_text,
                    html_message=mesaj_html,
                    fail_silently=True
                )
                
                print(f"!!! EROARE CRITICĂ: {e}")
                form.add_error(None, "Eroare internă. Administratorii au fost notificați.")







def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            
            cod_unic = str(uuid.uuid4())
            user.cod = cod_unic
            user.email_confirmat = False
            user.save()
            
            subiect = "Confirmare cont - Tankeria"
            link_confirmare = request.build_absolute_uri(reverse('confirma_mail', args=[user.cod]))
            
            context_email = {
                'user': user,
                'link_confirmare': link_confirmare
            }
            
            html_message = render_to_string('confirmare_email.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subiect,
                plain_message,
                settings.DEFAULT_FORM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False
            )

            messages.success(request, 'Cont creat! Te rugăm să verifici email-ul pentru confirmare.')
            return redirect('login') 
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form, 'ip_address': get_ip_address(request)}
    return render(request, 'autentificare/register.html', context)


def confirma_mail(request, cod):
    try:
        user = CustomUser.objects.get(cod=cod)
        
        if user.email_confirmat:
            messages.info(request, "Adresa de email este deja confirmată.")
        else:
            user.email_confirmat = True
            user.save()
            messages.success(request, "Email confirmat cu succes! Acum te poți loga.")
            
    except CustomUser.DoesNotExist:
        messages.error(request, "Cod de confirmare invalid sau expirat.")
        
    return redirect('login')



def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        
        ip = get_ip_address(request)
        cache_key = f"failed_login_{ip}"
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if not user.email_confirmat:
                    if user.blocat:
                        messages.error(request, 'Contul tău a fost blocat de un moderator. Nu te poți loga.')
                        return redirect('login')
                
                cache.delete(cache_key)
                logger.info(f"INFO: Utilizatorul {user.username} s-a logat cu succes.")
                login(request, user)
                
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24)
                else:
                    request.session.set_expiry(0)
                request.session['profil'] = {
                    'username': user.username,
                    'email': user.email,
                    'nume': user.first_name,
                    'prenume': user.last_name,
                    'telefon': user.telefon,
                    'data_nasterii': user.data_nasterii.isoformat() if user.data_nasterii else None,
                    'oras': user.adresa_oras,
                }
                
                messages.info(request, f'Te-ai logat cu succes ca {username}.')
                return redirect('profile')
            
            else:
                username_incercat = form.cleaned_data.get('username', 'necunoscut')
                logger.error(f"ERROR: Tentativa de logare esuata pentru user: {form.cleaned_data.get('username')}")
                attempts = cache.get(cache_key, [])
                current_time = time.time()
                
                attempts = [t for t in attempts if current_time - t < 120]
                
                attempts.append(current_time)
                
                cache.set(cache_key, attempts, timeout=300)
                
                if len(attempts) >= 3:
                    logger.critical(f"CRITICAL: Posibil atac Brute-Force de la IP: {ip}")
                    subiect = "Logari suspecte"
                    mesaj_text = f"Username folosit: {username_incercat}\nIP: {ip}\nAu fost detectate 3 incercari esuate in ultimele 2 minute."
                    
                    mesaj_html = f"""
                        <h1 style="color: red;">{subiect}</h1>
                        <p><strong>Username incercat:</strong> {username_incercat}</p>
                        <p><strong>IP Sursă:</strong> {ip}</p>
                        <p>Sistemul a detectat incercari repetate de autentificare esuata.</p>
                    """
                    
                    mail_admins(
                        subject=subiect,
                        message=mesaj_text,
                        html_message=mesaj_html,
                        fail_silently=True
                    )
                    
                messages.error(request, 'Nume de utilizator sau parolă incorectă.')
                
        else:
            messages.error(request, 'Formular invalid. Verifică datele introduse.')

    else:
        form = CustomLoginForm()
        
    context = {'form': form, 'ip_address': get_ip_address(request)}
    return render(request, 'autentificare/login.html', context)

@login_required
def logout_view(request):
    try:
        permisiune = Permission.objects.get(codename='vizualizeaza_oferta')
        request.user.user_permissions.remove(permisiune)
    except Permission.DoesNotExist:
        pass

    if 'profil' in request.session:
        del request.session['profil']
        
    logout(request)
    messages.info(request, 'Te-ai delogat cu succes.')
    return redirect('index')


@login_required
def profile_view(request):
    profil_data = request.session.get('profil', {})
    
    context = {
        'profil': profil_data,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'autentificare/profile.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Parola a fost schimbata cu succes!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
        
    context = {'form': form, 'ip_address': get_ip_address(request)}
    return render(request, 'autentificare/change_password.html', context)

def promotii_view(request):
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            promotie = form.save(commit=False)
            
            zile = form.cleaned_data['valabilitate_zile']
            promotie.data_expirare = timezone.now() + datetime.timedelta(days=zile)
            promotie.save()
            
            form.save_m2m() 
            
            categorii_selectate = form.cleaned_data['categorii']
            K = 3
            
            mesaje_de_trimis = []
            
            for categorie in categorii_selectate:
                users_target = CustomUser.objects.filter(
                    vizualizare__produs__id_categorie=categorie
                ).annotate(
                    nr_viz=Count('vizualizare')
                ).filter(nr_viz__gte=K).distinct()
                
                nume_template = f"template_{categorie.nume_categorie}.txt"
                cale_template = os.path.join(settings.BASE_DIR, 'proiectapp', 'templates', 'email', nume_template)
                
                continut_template = ""
                try:
                    with open(cale_template, 'r') as f:
                        continut_template = f.read()
                except FileNotFoundError:
                    continut_template = "Salut! Avem o promoție specială: {subiect}. Expiră la {data_expirare}. Detalii: {mesaj}"

                for user in users_target:
                    mesaj_final = continut_template.format(
                        nume_client=f"{user.first_name} {user.last_name}",
                        subiect=promotie.subiect,
                        data_expirare=promotie.data_expirare.strftime('%d-%m-%Y'),
                        mesaj=promotie.mesaj,
                        alte_date="Reduceri masive la tancuri!"
                    )
                    
                    mesaje_de_trimis.append((
                        promotie.subiect,
                        mesaj_final,
                        settings.DEFAULT_FORM_EMAIL,
                        [user.email]
                    ))
            
            if mesaje_de_trimis:
                send_mass_mail(tuple(mesaje_de_trimis), fail_silently=False)
                messages.success(request, f"Promoția a fost trimisă la {len(mesaje_de_trimis)} utilizatori!")
            else:
                messages.warning(request, "Nu au fost găsiți utilizatori eligibili (care au vizualizat produse).")
                
            return redirect('promotii')
            
    else:
        form = PromotieForm()

    return render(request, 'promotii.html', {'form': form})


def view_403(request, exception=None):

    cnt = request.session.get('cnt_403', 0) + 1
    request.session['cnt_403'] = cnt
    
    context = {
        'titlu': '',
        'mesaj_personalizat': 'Nu aveți permisiunea de a accesa această resursă.',
        'count': cnt,
        'n_max': settings.N_MAX_403
    }
    
    return render(request, '403.html', context, status=403)

def return_403_custom(request, titlu, mesaj):
    cnt = request.session.get('cnt_403', 0) + 1
    request.session['cnt_403'] = cnt
    context = {
        'titlu': titlu,
        'mesaj_personalizat': mesaj,
        'count': cnt,
        'n_max': getattr(settings, 'N_MAX_403', 5)
    }
    return render(request, '403.html', context, status=403)

def accesare_oferta(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    content_type = ContentType.objects.get_for_model(CustomUser)
    permisiune, created = Permission.objects.get_or_create(
        codename='vizualizeaza_oferta',
        defaults={
            'name': 'Poate vizualiza oferta speciala',
            'content_type': content_type,
        }
    )
    request.user.user_permissions.add(permisiune)
    
    return redirect('oferta')

def oferta_view(request):
    if not request.user.is_authenticated or not request.user.has_perm('proiectapp.vizualizeaza_oferta'):
        cnt = request.session.get('cnt_403', 0) + 1
        request.session['cnt_403'] = cnt
        
        context = {
            'titlu': 'Eroare afisare oferta',
            'mesaj_personalizat': 'Nu ai voie să vizualizezi oferta',
            'count': cnt,
            'n_max': getattr(settings, 'N_MAX_403', 5)
        }
        return render(request, '403.html', context, status=403)

    return render(request, 'oferta.html')