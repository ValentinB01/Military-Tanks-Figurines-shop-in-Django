import os
import django
from datetime import date
import sys
from pathlib import Path
CURRENT_FILE_PATH = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE_PATH.parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proiect.settings')
django.setup()
from proiectapp.models import * 



def populate_tancuri():
    print("Incep popularea bazei de date cu TANCURI...")
    categorii = [
        {'nume_categorie': 'Tancuri Americane', 'descriere': 'Modele de tancuri din Statele Unite', 'activa': True},
        {'nume_categorie': 'Tancuri Germane', 'descriere': 'Modele de tancuri germane', 'activa': True},
        {'nume_categorie': 'Tancuri Rusești', 'descriere': 'Modele de tancuri sovietice si rusesti', 'activa': True},
        {'nume_categorie': 'Tancuri Britanice', 'descriere': 'Modele de tancuri britanice', 'activa': True}
    ]
    
    for cat_data in categorii:
        cat, created = Categorie.objects.get_or_create(**cat_data)
        print(f"{'Creata' if created else 'Exista'} categorie: {cat.nume_categorie}")
    
    producatori = [
        {'nume_producator': 'Tamiya', 'tara_origine': 'Japonia', 'email': 'contact@tamiya.com', 'activ': True},
        {'nume_producator': 'Revell', 'tara_origine': 'Germania', 'email': 'info@revell.de', 'activ': True},
        {'nume_producator': 'Italeri', 'tara_origine': 'Italia', 'email': None, 'activ': True},
        {'nume_producator': 'Dragon Models', 'tara_origine': 'Hong Kong', 'telefon': None, 'activ': True}
    ]
    
    for prod_data in producatori:
        prod, created = Producator.objects.get_or_create(**prod_data)
        print(f"{'Creata' if created else 'Exista'} producator: {prod.nume_producator}")
    
    serii_data = [
        {'nume_serie': 'Tancuri WWII', 'an_lansare': 2020, 'scala': '1:35', 'id_producator': Producator.objects.get(nume_producator='Tamiya')},
        {'nume_serie': 'Tancuri Razboiul Rece', 'an_lansare': 2019, 'scala': '1:48', 'id_producator': Producator.objects.get(nume_producator='Revell')},
        {'nume_serie': 'Tancuri Usoare', 'an_lansare': 2021, 'scala': '1:72', 'id_producator': Producator.objects.get(nume_producator='Italeri')},
        {'nume_serie': 'Tancuri Grele', 'an_lansare': 2018, 'scala': '1:35', 'id_producator': Producator.objects.get(nume_producator='Dragon Models')},
        {'nume_serie': 'Tancuri Moderne', 'an_lansare': 2022, 'scala': '1:100', 'id_producator': Producator.objects.get(nume_producator='Tamiya')},
    ]
    
    for ser_data in serii_data:
        ser, created = Seria.objects.get_or_create(**ser_data)
        print(f"{'Creat' if created else 'Exista'} serie: {ser.nume_serie} ({ser.scala})")
    
    seturi_accesorii = [ 
        {'nume_set': 'Set Camuflaj Avansat', 'nr_piese': 3, 'compatibilitate': 'Toate modelele', 'tip_accesorii': 'CAM'},
        {'nume_set': 'Set Vopsele Militare', 'nr_piese': 8, 'compatibilitate': 'Culori standard NATO', 'tip_accesorii': 'VOP'},
        {'nume_set': 'Set Lanturi de Otel', 'nr_piese': 3, 'compatibilitate': 'Tancuri WWII', 'tip_accesorii': 'LANT'},
        {'nume_set': 'Set Unelte', 'nr_piese': 12, 'compatibilitate': 'Modele la scara mica', 'tip_accesorii': 'UNEL'},
        {'nume_set': 'Set Display Premium', 'nr_piese': 5, 'compatibilitate': 'Toate modelele', 'tip_accesorii': 'ALT'},
    ]
    
    for set_data in seturi_accesorii:
        set_acc, created = SetAccessorii.objects.get_or_create(**set_data)
        print(f"{'Creat' if created else 'Exista'} set: {set_acc.nume_set}")
    
    materiale = [
        {'tip_material': 'Plastic Polistiren', 'culoare': 'Gri', 'textura': 'NETE', 'rezistent_la_apa': False},
        {'tip_material': 'Plastic ABS', 'culoare': 'Alb', 'textura': 'MAT', 'rezistent_la_apa': True},
        {'tip_material': 'Metal Turnat', 'culoare': None, 'textura': 'MAT', 'rezistent_la_apa': True},  # CULOARE NULL
        {'tip_material': 'Resina', 'culoare': 'Transparent', 'textura': 'STR', 'rezistent_la_apa': True},
        {'tip_material': 'Cauciuc Sintetic', 'culoare': 'Negru', 'textura': 'TEXT', 'rezistent_la_apa': False},
    ]
    
    for mat_data in materiale:
        mat, created = Material.objects.get_or_create(**mat_data)
        print(f"{'Creat' if created else 'Exista'} material: {mat.tip_material}")

    tancuri = [
        {
            'nume_figurina': 'M1A2 Abrams',
            'pret': 450.00,
            'greutate': 1.2,
            'stoc_disponibil': 8,
            'data_lansare': date(2023, 5, 15),
            'tara_origine': 'USA',
            'stare': 'NOU',
            'descriere': None,
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Americane'),
            'id_producator': Producator.objects.get(nume_producator='Tamiya'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri Moderne'),
        },
        {
            'nume_figurina': 'Tiger I',
            'pret': 380.50,
            'greutate': 0.9,
            'stoc_disponibil': 5,
            'data_lansare': date(2022, 11, 20),
            'tara_origine': 'GER', 
            'stare': 'COL',
            'descriere': None,
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Germane'),
            'id_producator': Producator.objects.get(nume_producator='Revell'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri WWII'),
        },
        {
            'nume_figurina': 'T-34/85',
            'pret': 295.75,
            'greutate': 0.7,
            'stoc_disponibil': 12,
            'data_lansare': date(2023, 2, 10),
            'tara_origine': 'RUS',
            'stare': 'NOU',
            'descriere': None,
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Rusesti'),
            'id_producator': Producator.objects.get(nume_producator='Italeri'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri WWII'),
        },
        {
            'nume_figurina': 'M4A3E8 Sherman',
            'pret': 320.00,
            'greutate': 0.8,
            'stoc_disponibil': 0,
            'data_lansare': date(2021, 8, 30),
            'tara_origine': 'USA',
            'stare': 'FOL',
            'descriere': 'Tanc Sherman varianta îmbunatatita',
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Americane'),
            'id_producator': Producator.objects.get(nume_producator='Dragon Models'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri Grele'),
        },
        {
            'nume_figurina': 'Panther Ausf.G',
            'pret': 415.25,
            'greutate': 0.6,
            'stoc_disponibil': 3,
            'data_lansare': date(2023, 7, 5),
            'tara_origine': 'GER',
            'stare': 'RES',
            'descriere': None,
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Germane'),
            'id_producator': Producator.objects.get(nume_producator='Tamiya'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri WWII'),
        },
        {
            'nume_figurina': 'Centurion Mk.III',
            'pret': 355.80,
            'greutate': 1.1,
            'stoc_disponibil': 6,
            'data_lansare': date(2022, 12, 15),
            'tara_origine': 'UK',
            'stare': 'NOU',
            'descriere': 'Tanc britanic de infanterie',
            'id_categorie': Categorie.objects.get(nume_categorie='Tancuri Britanice'),
            'id_producator': Producator.objects.get(nume_producator='Revell'),
            'id_serie': Seria.objects.get(nume_serie='Tancuri Razboiul Rece'),
        },
    ]
    
    for tank_data in tancuri:
        tank, created = Figurina.objects.get_or_create(**tank_data)
        print(f"{'Creata' if created else 'Exista'} figurina: {tank.nume_figurina}")
        
        if tank.nume_figurina == 'M1A2 Abrams':
            tank.materiale.add(
                Material.objects.get(tip_material='Plastic Polistiren'),
                through_defaults={'procentaj': 80.00}
            )
            tank.materiale.add(
                Material.objects.get(tip_material='Metal Turnat'),
                through_defaults={'procentaj': 20.00}
            )
            tank.seturi_accesorii.add(
                SetAccessorii.objects.get(nume_set='Set Camuflaj Avansat'),
                through_defaults={'compatibil_perfect': True}
            )
        
        elif tank.nume_figurina == 'Tiger I':
            tank.materiale.add(
                Material.objects.get(tip_material='Plastic ABS'),
                through_defaults={'procentaj': 100.00}
            )
            tank.seturi_accesorii.add(
                SetAccessorii.objects.get(nume_set='Set Lanturi de Otel'),
                through_defaults={'compatibil_perfect': True}
            )
        
        elif tank.nume_figurina == 'T-34/85':
            tank.materiale.add(
                Material.objects.get(tip_material='Plastic Polistiren'),
                through_defaults={'procentaj': 70.00}
            )
            tank.materiale.add(
                Material.objects.get(tip_material='Resina'),
                through_defaults={'procentaj': 30.00}
            )
            
if __name__ == '__main__':
    populate_tancuri()