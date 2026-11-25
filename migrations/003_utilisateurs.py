# Migration 003 : table des utilisateurs avec mots de passe hachés
# À lancer UNE SEULE FOIS sur le serveur :  python3 migrations/003_utilisateurs.py
import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'database.db'))
conn.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    mot_de_passe_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user'))
)''')
for login, mdp, role in [('admin', 'password', 'admin'), ('user', '12345', 'user')]:
    conn.execute('INSERT OR IGNORE INTO utilisateurs (login, mot_de_passe_hash, role) VALUES (?, ?, ?)',
                 (login, generate_password_hash(mdp), role))
conn.commit()
for row in conn.execute('SELECT id, login, role, substr(mot_de_passe_hash, 1, 25) FROM utilisateurs'):
    print(row)
conn.close()
print("✅ Table utilisateurs prête")
