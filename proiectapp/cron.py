import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail, send_mass_mail, mail_admins
from .models import CustomUser, AccessLog, Figurina, Seria

logger = logging.getLogger('proiectapp')

def sterge_utilizatori_neconfirmati():
    limita_timp = timezone.now() - timedelta(minutes=settings.K_MINUTE_STERGERE)
    
    users_to_delete = CustomUser.objects.filter(
        email_confirmat=False,
        date_joined__lt=limita_timp
    )
    
    count = users_to_delete.count()
    if count > 0:
        for user in users_to_delete:
            logger.info(f"INFO: S-a sters automat utilizatorul neconfirmat: {user.username} (Email: {user.email})")
            user.delete()
        print(f"Task 1: Au fost stersi {count} utilizatori neconfirmati.")
    else:
        print("Task 1: Nu exista utilizatori de sters.")

def trimite_newsletter():
    serie_promovata = Seria.objects.filter(disponibilitate=True).order_by('?').first()
    
    if not serie_promovata:
        return

    subiect = f"Noutati Tankeria: Descopera seria {serie_promovata.nume_serie}!"
    mesaj_body = (
        f"Salutare colectionarule,\n\n"
        f"Saptamana aceasta aducem in prim plan seria: {serie_promovata.nume_serie}.\n"
        f"Scara: {serie_promovata.scala}\n"
        f"Aceasta serie istorica contine modele detaliate precum {serie_promovata.descriere}.\n\n"
        f"Intra pe site si completeaza-ti colectia!\n"
        f"Echipa Military Tanks"
    )

    limita_vechime = timezone.now() - timedelta(minutes=settings.X_VECHIME_MINUTE)
    destinatari = CustomUser.objects.filter(
        date_joined__lt=limita_vechime,
        email_confirmat=True,
        blocat=False
    )

    mesaje = []
    for user in destinatari:
        mesaje.append((
            subiect,
            mesaj_body,
            settings.DEFAULT_FORM_EMAIL,
            [user.email]
        ))

    if mesaje:
        send_mass_mail(tuple(mesaje), fail_silently=True)
        logger.info(f"INFO: Newsletter trimis automat catre {len(mesaje)} utilizatori. Subiect: {serie_promovata.nume_serie}")

def curata_loguri_vechi():
    zile_pastrare = 7
    limita = timezone.now() - timedelta(days=zile_pastrare)
    
    logs_sterse = AccessLog.objects.filter(timestamp__lt=limita)
    numar = logs_sterse.count()
    
    if numar > 0:
        logs_sterse.delete()
        logger.warning(f"WARNING: Task de mentenanta. S-au sters {numar} intrari vechi din AccessLog.")

def raport_stoc_critic():
    produse_critice = Figurina.objects.filter(stoc_disponibil__lt=3)
    
    if produse_critice.exists():
        lista_produse = "\n".join([f"- {p.nume_figurina} (Stoc: {p.stoc_disponibil})" for p in produse_critice])
        
        subiect = "RAPORT AUTOMAT: Stocuri Critice"
        mesaj = (
            f"Urmatoarele produse au stoc limitat si necesita reaprovizionare:\n\n"
            f"{lista_produse}\n\n"
            f"Acest mesaj este generat automat."
        )
        
        mail_admins(subiect, mesaj, fail_silently=True)
        logger.info("INFO: Raportul de stoc critic a fost trimis administratorilor.")