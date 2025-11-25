#!/bin/bash

# 1. Configurare Variabile Baza de Date (din settings.py)
DB_NAME="proiectdb"
DB_USER="valentin"
DB_HOST="localhost"
DB_PORT="5432"
DB_PASS="1234" # Parola din settings.py

# 2. Configurare Director și Nume Fișier
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/backup_data_$TIMESTAMP.sql"

# Creăm directorul de backup dacă nu există
mkdir -p "$BACKUP_DIR"

# 3. Lista tabelelor din models.py (Django adaugă automat prefixul numelui aplicației)
# Ordinea contează uneori la restore (din cauza cheilor străine), dar pg_dump gestionează bine asta.
TABLES=(
    "proiectapp_customuser"
    "proiectapp_categorie"
    "proiectapp_producator"
    "proiectapp_seria"
    "proiectapp_setaccessorii"
    "proiectapp_material"
    "proiectapp_figurina"
    "proiectapp_figurinamaterial"
    "proiectapp_figurinasetaccesorii"
    "proiectapp_accesslog"
)

# Construim argumentele pentru tabele (-t tabel1 -t tabel2 ...)
TABLE_ARGS=""
for table in "${TABLES[@]}"; do
    TABLE_ARGS="$TABLE_ARGS -t $table"
done

# 4. Exportul efectiv folosind pg_dump
# --column-inserts: Generează INSERT INTO table (col1, col2) VALUES ...
# --data-only: Nu exportă structura (CREATE TABLE), ci doar datele
# --no-owner: Nu include comenzi de setare a proprietarului

echo "Se incepe generarea backup-ului SQL pentru tabelele aplicatiei..."

# Exportăm variabila de mediu pentru parolă ca să nu o ceară interactiv
export PGPASSWORD=$DB_PASS

pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER \
    --column-inserts \
    --data-only \
    --no-owner \
    $TABLE_ARGS \
    $DB_NAME > "$BACKUP_FILE"

# Ștergem variabila de mediu pentru securitate
unset PGPASSWORD

# 5. Verificare
if [ -f "$BACKUP_FILE" ]; then
    echo "Succes! Backup creat la: $BACKUP_FILE"
    # Afișăm primele 5 linii ca exemplu
    echo "Previzualizare continut:"
    head -n 5 "$BACKUP_FILE"
else
    echo "Eroare! Fisierul de backup nu a fost creat."
fi