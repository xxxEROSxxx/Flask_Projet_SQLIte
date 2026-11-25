# ---------------------------------------------------------------
#  Données d'exemple du projet bibliothèque
#  (utilisées par create_db.py et par la migration 004)
# ---------------------------------------------------------------
from werkzeug.security import generate_password_hash

COMPTES = [
    # login, mot de passe, rôle, nom, prénom
    ('admin', 'password', 'admin', 'ADMIN', 'Bibliothécaire'),
    ('user', '12345', 'user', 'LECTEUR', 'Test'),
    ('alice', 'alice123', 'user', 'MARTIN', 'Alice'),
    ('bob', 'bob123', 'user', 'DURAND', 'Bob'),
]

LIVRES = [
    # titre, auteur, isbn, année, genre, nb_exemplaires
    ('Le Petit Prince', 'Antoine de Saint-Exupéry', '9782070612758', 1943, 'Conte', 3),
    ('Les Misérables', 'Victor Hugo', '9782253096344', 1862, 'Roman', 2),
    ('Germinal', 'Émile Zola', '9782253004226', 1885, 'Roman', 1),
    ('L\'Étranger', 'Albert Camus', '9782070360024', 1942, 'Roman', 2),
    ('1984', 'George Orwell', '9782070368228', 1949, 'Science-fiction', 2),
    ('Fondation', 'Isaac Asimov', '9782070415700', 1951, 'Science-fiction', 1),
    ('Le Seigneur des anneaux', 'J. R. R. Tolkien', '9782266282369', 1954, 'Fantasy', 2),
    ('Harry Potter à l\'école des sorciers', 'J. K. Rowling', '9782070584628', 1997, 'Fantasy', 3),
    ('Le Comte de Monte-Cristo', 'Alexandre Dumas', '9782253098058', 1844, 'Aventure', 1),
    ('Vingt mille lieues sous les mers', 'Jules Verne', '9782253006329', 1870, 'Aventure', 2),
    ('Sapiens', 'Yuval Noah Harari', '9782226257017', 2011, 'Essai', 1),
    ('Astérix le Gaulois', 'Goscinny et Uderzo', '9782012101333', 1961, 'BD', 2),
]

# Emprunts de démonstration : (login, titre, il y a N jours, rendu ?)
EMPRUNTS = [
    ('alice', 'Le Petit Prince', 3, False),
    ('alice', '1984', 20, True),
    ('bob', 'Germinal', 20, False),          # en retard (prévu à 14 jours)
    ('bob', 'Le Petit Prince', 30, True),
    ('user', 'Fondation', 5, False),
]


def remplir(conn):
    """Ajoute les comptes, les livres et les emprunts d'exemple (sans doublon)."""
    for login, mdp, role, nom, prenom in COMPTES:
        existe = conn.execute('SELECT id FROM utilisateurs WHERE login = ?', (login,)).fetchone()
        if existe:
            conn.execute('UPDATE utilisateurs SET nom = ?, prenom = ? WHERE login = ?', (nom, prenom, login))
        else:
            conn.execute('INSERT INTO utilisateurs (login, mot_de_passe_hash, role, nom, prenom) VALUES (?, ?, ?, ?, ?)',
                         (login, generate_password_hash(mdp), role, nom, prenom))

    if conn.execute('SELECT COUNT(*) FROM livres').fetchone()[0] == 0:
        conn.executemany('INSERT INTO livres (titre, auteur, isbn, annee, genre, nb_exemplaires) VALUES (?, ?, ?, ?, ?, ?)',
                         LIVRES)

    if conn.execute('SELECT COUNT(*) FROM emprunts').fetchone()[0] == 0:
        for login, titre, jours, rendu in EMPRUNTS:
            uid = conn.execute('SELECT id FROM utilisateurs WHERE login = ?', (login,)).fetchone()[0]
            lid = conn.execute('SELECT id FROM livres WHERE titre = ?', (titre,)).fetchone()[0]
            conn.execute(f'''INSERT INTO emprunts (livre_id, utilisateur_id, date_emprunt, date_retour_prevue, date_retour)
                             VALUES (?, ?, datetime('now', '-{jours} days'), date('now', '-{jours} days', '+14 days'),
                                     {"datetime('now', '-1 days')" if rendu else 'NULL'})''', (lid, uid))
