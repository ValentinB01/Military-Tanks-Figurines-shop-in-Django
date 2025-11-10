from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Categorie, Producator, Figurina, Seria
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from .models import AccessLog
from collections import OrderedDict
import datetime
from django.core.paginator import Paginator


def log_view(request):
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

def index(request):
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

def produse(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'in_lucru.html', context)

def contact(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'in_lucru.html', context)

def cos_virtual(request):
    context = {'ip_address': get_ip_address(request)}
    return render(request, 'in_lucru.html', context)



def produse(request):
    figurine_list = Figurina.objects.select_related('id_categorie'). all()

    params_get = request.GET.copy()

    sort_by = request.GET.get('sort')
    if sort_by == 'a':
        figurine_list = figurine_list.order_by('pret')
    elif sort_by == 'd':
        figurine_list = figurine_list.order_by('-pret')
    else:
        figurine_list = figurine_list.order_by('nume_figurina')
    
    paginator = Paginator(figurine_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
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
        'ip_address': get_ip_address(request)
    }
    return render(request, 'produse.html', context)

def produs_detaliu(request, id_figurina):
    figurina = get_object_or_404(Figurina, id_figurina=id_figurina)
    context = {
        'fig': figurina,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'produs_detaliu.html', context)

def categorie_detaliu(request, nume_categorie):
    categorie = get_object_or_404(Categorie, nume_categorie=nume_categorie)
    produse_in_categorie = Figurina.objects.filter(id_categorie=categorie)
    context = {
        'cat': categorie,
        'produse': produse_in_categorie,
        'ip_address': get_ip_address(request)
    }
    return render(request, 'categorie_detaliu.html', context)

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