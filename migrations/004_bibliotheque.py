# Migration 004 : tables du projet bibliothèque + données d'exemple
# À lancer UNE SEULE FOIS sur le serveur :  python3 migrations/004_bibliotheque.py
# (sans effacer les clients et les commandes des ateliers)
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from donnees_bibliotheque import remplir

conn = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))

# 1. Table utilisateurs : création si besoin + colonnes nom et prénom
conn.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user'))
)''')
colonnes = [c[1] for c in conn.execute('PRAGMA table_info(utilisateurs)')]
for col in ('nom', 'prenom'):
    if col not in colonnes:
        conn.execute(f'ALTER TABLE utilisateurs ADD COLUMN {col} TEXT')

# 2. Tables livres et emprunts
conn.execute('''CREATE TABLE IF NOT EXISTS livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    isbn TEXT,
    annee INTEGER,
    genre TEXT,
    nb_exemplaires INTEGER NOT NULL DEFAULT 1 CHECK (nb_exemplaires >= 0)
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    utilisateur_id INTEGER NOT NULL,
    date_emprunt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_retour_prevue DATE NOT NULL,
    date_retour TIMESTAMP,
    FOREIGN KEY (livre_id) REFERENCES livres (id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id)
)''')

# 3. Données d'exemple
remplir(conn)
conn.commit()

print("Utilisateurs :", [r[0] for r in conn.execute('SELECT login FROM utilisateurs')])
print("Livres       :", conn.execute('SELECT COUNT(*) FROM livres').fetchone()[0])
print("Emprunts     :", conn.execute('SELECT COUNT(*) FROM emprunts').fetchone()[0])
conn.close()
print("✅ Bibliothèque prête")
