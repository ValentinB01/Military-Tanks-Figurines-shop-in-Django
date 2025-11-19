#!/bin/bash
echo "Pornire backup SQL (Varianta Automata: Linux FOR)..."

# Seteaza variabilele din settings.py
DB_NAME="proiectdb"
DB_USER="valentin"
DB_HOST="localhost"
DB_PORT="5432"
OUTPUT_FILE="proiectapp/backup_inserts_auto.sql"

# Seteaza parola
export PGPASSWORD='1234'

# Comanda SQL pentru a gasi toate tabelele noastre
SQL_QUERY="SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'proiectapp_%'"

echo "Creare fisier gol: $OUTPUT_FILE"
# Sterge backup-ul vechi (creeaza un fisier gol)
> "$OUTPUT_FILE"

echo "Se interogheaza baza de date pentru lista de tabele..."
echo "Se genereaza comenzile INSERT pentru fiecare tabel..."

# --- LINIA MODIFICATĂ ---
# Rulăm comanda psql direct aici, cu "$SQL_QUERY" între ghilimele
# pentru a fi tratat ca un singur argument.
for t in $(psql -U $DB_USER -h $DB_HOST -d $DB_NAME -t -c "$SQL_QUERY")
do
    echo "...Exporting data from $t"
    pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -t "$t" --data-only --column-inserts >> "$OUTPUT_FILE"
done
# --- SFÂRȘIT MODIFICARE ---

# Sterge parola din mediu
unset PGPASSWORD

echo "Backup SQL (Automat) finalizat! Fisier salvat in: $OUTPUT_FILE"