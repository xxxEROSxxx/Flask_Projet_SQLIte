# ---------------------------------------------------------------
#  Atelier Flask + SQLite
# ---------------------------------------------------------------
#  Ce fichier est le "cerveau" de votre application : il reçoit
#  les demandes des navigateurs, interroge la base de données
#  et fabrique les réponses.
#
#  Vous allez le compléter petit à petit, exercice après exercice.
#  Les consignes sont dans le dossier "exercices/".
# ---------------------------------------------------------------

import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour signer les sessions (à cacher par la suite)

# Chemin ABSOLU vers la base de données.
# Sur PythonAnywhere, le serveur ne démarre pas forcément dans le dossier
# du projet : un simple 'database.db' créerait une base vide ailleurs !
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db():
    """Ouvre une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # pour écrire row['nom'] au lieu de row[2]
    conn.execute('PRAGMA foreign_keys = ON')  # faire respecter les clés étrangères
    return conn


# Fonction pour savoir si l'utilisateur s'est authentifié
def est_authentifie():
    return session.get('authentifie')


# Exercice 8 : vérifier le rôle de l'utilisateur connecté
def a_le_role(*roles):
    """Renvoie True si l'utilisateur connecté a l'un des rôles indiqués."""
    return session.get('role') in roles


@app.route('/')
def hello_world():
    return render_template('accueil.html')


@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

    # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"


@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        conn = get_db()
        compte = conn.execute('SELECT * FROM utilisateurs WHERE login = ?',
                              (request.form['username'],)).fetchone()
        conn.close()
        if compte and check_password_hash(compte['mot_de_passe_hash'], request.form['password']):
            session['authentifie'] = True
            session['utilisateur'] = compte['login']
            session['role'] = compte['role']
            session['user_id'] = compte['id']
            flash(f"Bienvenue {compte['login']} !", "ok")
            return redirect(url_for('hello_world'))
        return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)


@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')


@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchone()  # une seule ligne (ou None si l'id n'existe pas)
    if not data:
        conn.close()
        return "<h2>Client introuvable</h2>", 404
    # Exercice 7 : 2e requête pour les commandes du client
    cursor.execute('SELECT * FROM commandes WHERE client_id = ? ORDER BY date_commande DESC', (post_id,))
    commandes = cursor.fetchall()
    conn.close()
    return render_template('fiche_client.html', client=data, commandes=commandes)


@app.route('/consultation/')
def ReadBDD():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients ORDER BY nom;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    return render_template('formulaire.html')  # afficher le formulaire


@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    # Exercice 4 : on récupère les 3 champs et on les nettoie
    nom = request.form.get('nom', '').strip().upper()
    prenom = request.form.get('prenom', '').strip()
    adresse = request.form.get('adresse', '').strip()
    telephone = request.form.get('telephone', '').strip()

    # Validation côté serveur : on ne fait jamais confiance au navigateur
    if not nom or not prenom or not adresse:
        return render_template('formulaire.html', erreur="Tous les champs sont obligatoires."), 400

    conn = get_db()
    cursor = conn.cursor()
    # On n'indique plus "created" : SQLite met la date du jour (DEFAULT CURRENT_TIMESTAMP)
    cursor.execute('INSERT INTO clients (nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?)',
                   (nom, prenom, adresse, telephone))
    conn.commit()
    conn.close()
    return redirect('/consultation/')


# ---------------------------------------------------------------
#  Ajoutez vos nouvelles routes ci-dessous 👇
# ---------------------------------------------------------------

# Exercice 3 - Partie A : recherche par nom exact (requête protégée avec ?)
@app.route('/fiche_nom/<nom>')
def fiche_nom(nom):
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)


# Exercice 3 - Partie B + Défi : formulaire de recherche avec choix du tri
TRIS_AUTORISES = {'nom': 'nom', 'prenom': 'prenom', 'date': 'created'}


@app.route('/recherche')
def recherche():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    q = request.args.get('q', '').strip()
    tri = request.args.get('tri', 'nom')
    colonne = TRIS_AUTORISES.get(tri, 'nom')  # seules les colonnes de la liste sont acceptées
    data = []
    if q:
        conn = get_db()
        cursor = conn.cursor()
        motif = '%' + q + '%'
        cursor.execute('SELECT * FROM clients WHERE nom LIKE ? OR prenom LIKE ? ORDER BY ' + colonne,
                       (motif, motif))
        data = cursor.fetchall()
        conn.close()
    return render_template('recherche.html', q=q, data=data, tri=tri)



# Exercice 5 - Partie A + Exercice 7 - Partie D : supprimer un client (POST uniquement)
@app.route('/supprimer_client/<int:id>', methods=['POST'])
def supprimer_client(id):
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    conn = get_db()
    try:
        conn.execute('DELETE FROM clients WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.IntegrityError:
        nb = conn.execute('SELECT COUNT(*) FROM commandes WHERE client_id = ?', (id,)).fetchone()[0]
        return (f"<h2>Impossible : ce client a {nb} commande(s).</h2>"
                f"<p><a href='/fiche_client/{id}'>Voir sa fiche</a></p>"), 409
    finally:
        conn.close()  # exécuté dans TOUS les cas, même après le return
    return redirect('/consultation/')


# Exercice 5 - Partie B : modifier un client (GET = formulaire pré-rempli, POST = enregistrer)
@app.route('/modifier_client/<int:id>', methods=['GET', 'POST'])
def modifier_client(id):
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute('UPDATE clients SET nom = ?, prenom = ?, adresse = ?, telephone = ? WHERE id = ?',
                       (request.form['nom'].strip().upper(),
                        request.form['prenom'].strip(),
                        request.form['adresse'].strip(),
                        request.form.get('telephone', '').strip(),
                        id))
        conn.commit()
        conn.close()
        return redirect('/consultation/')

    cursor.execute('SELECT * FROM clients WHERE id = ?', (id,))
    client = cursor.fetchone()
    conn.close()
    if client is None:
        return "<h2>Client introuvable</h2>", 404
    return render_template('modifier_client.html', client=client)


# Exercice 7 - Partie C : toutes les commandes avec le nom du client (JOIN)
@app.route('/commandes/')
def liste_commandes():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    data = conn.execute('''
        SELECT commandes.id, commandes.client_id, clients.nom, clients.prenom,
               commandes.produit, commandes.montant
        FROM commandes
        JOIN clients ON commandes.client_id = clients.id
        ORDER BY commandes.id
    ''').fetchall()
    conn.close()
    return render_template('commandes.html', data=data)


# Exercice 7 - Partie C : nombre de commandes et total par client (LEFT JOIN + GROUP BY)
@app.route('/statistiques/')
def statistiques():
    if not a_le_role('user', 'admin'):
        return redirect(url_for('authentification'))
    conn = get_db()
    data = conn.execute('''
        SELECT clients.id, clients.nom, clients.prenom,
               COUNT(commandes.id) AS nb_commandes,
               COALESCE(SUM(commandes.montant), 0) AS total
        FROM clients
        LEFT JOIN commandes ON commandes.client_id = clients.id
        GROUP BY clients.id
        ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return render_template('statistiques.html', data=data)


# Exercice 7 - Défi : ajouter une commande depuis la fiche client
@app.route('/ajouter_commande/<int:client_id>', methods=['POST'])
def ajouter_commande(client_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))
    if not a_le_role('admin'):
        return "<h2>Accès refusé : réservé aux administrateurs</h2>", 403
    produit = request.form.get('produit', '').strip()
    montant = request.form.get('montant', '').strip()
    if not produit or not montant:
        return "<h2>Produit et montant obligatoires</h2>", 400
    conn = get_db()
    try:
        conn.execute('INSERT INTO commandes (client_id, produit, montant) VALUES (?, ?, ?)',
                     (client_id, produit, float(montant)))
        conn.commit()
    except (sqlite3.IntegrityError, ValueError):
        return "<h2>Commande impossible (client inexistant ou montant invalide)</h2>", 400
    finally:
        conn.close()
    return redirect(f'/fiche_client/{client_id}')


# Exercice 9 - Partie A + Défi 2 : liste des clients en JSON (filtre optionnel ?q=)
@app.get('/api/clients')
def api_liste_clients():
    q = request.args.get('q', '').strip()
    conn = get_db()
    if q:
        motif = '%' + q + '%'
        rows = conn.execute('SELECT * FROM clients WHERE nom LIKE ? OR prenom LIKE ? ORDER BY nom',
                            (motif, motif)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM clients ORDER BY nom').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# Exercice 9 - Partie A : un seul client en JSON
@app.get('/api/clients/<int:id>')
def api_un_client(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({'erreur': 'Client introuvable'}), 404
    return jsonify(dict(row))


# Exercice 9 - Parties B et C : créer un client en JSON (admin uniquement)
@app.post('/api/clients')
def api_creer_client():
    if not a_le_role('admin'):
        return jsonify({'erreur': 'Authentification administrateur requise'}), 401

    donnees = request.get_json(silent=True) or {}
    nom = str(donnees.get('nom', '')).strip().upper()
    prenom = str(donnees.get('prenom', '')).strip()
    adresse = str(donnees.get('adresse', '')).strip()

    if not nom or not prenom or not adresse:
        return jsonify({'erreur': 'Les champs nom, prenom et adresse sont obligatoires'}), 400

    conn = get_db()
    cursor = conn.execute('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)',
                          (nom, prenom, adresse))
    conn.commit()
    nouvel_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': nouvel_id, 'nom': nom, 'prenom': prenom, 'adresse': adresse}), 201


# Exercice 9 - Défi 1 : supprimer un client en JSON (admin uniquement)
@app.delete('/api/clients/<int:id>')
def api_supprimer_client(id):
    if not a_le_role('admin'):
        return jsonify({'erreur': 'Authentification administrateur requise'}), 401
    conn = get_db()
    try:
        cursor = conn.execute('DELETE FROM clients WHERE id = ?', (id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'erreur': 'Client introuvable'}), 404
    except sqlite3.IntegrityError:
        return jsonify({'erreur': 'Impossible : ce client a des commandes'}), 409
    finally:
        conn.close()
    return jsonify({'supprime': id})


# Exercice 9 - Défi 3 : page HTML qui appelle l'API en JavaScript
@app.route('/clients_api')
def clients_api():
    return render_template('clients_api.html')


# ===============================================================
#  📚 PROJET BIBLIOTHÈQUE (séquence 6)
# ===============================================================
from functools import wraps
from werkzeug.security import generate_password_hash

MAX_EMPRUNTS = 3          # R2 : 3 livres maximum en même temps
DUREE_PRET_JOURS = 14     # date de retour prévue = date d'emprunt + 14 jours

# Requête commune : chaque livre avec son nombre d'exemplaires disponibles (calculé, jamais stocké)
SQL_LIVRES_DISPO = '''
    SELECT livres.*,
           livres.nb_exemplaires - COUNT(emprunts.id) AS nb_disponibles
    FROM livres
    LEFT JOIN emprunts ON emprunts.livre_id = livres.id AND emprunts.date_retour IS NULL
'''


def connexion_requise(f):
    """Décorateur : la page est réservée aux utilisateurs connectés (user ou admin)."""
    @wraps(f)
    def verif(*args, **kwargs):
        if not a_le_role('user', 'admin'):
            flash("Connectez-vous pour accéder à cette page.", "erreur")
            return redirect(url_for('authentification'))
        return f(*args, **kwargs)
    return verif


def admin_requis(f):
    """Décorateur : la page est réservée aux administrateurs (R4 : code 403 sinon)."""
    @wraps(f)
    def verif(*args, **kwargs):
        if not est_authentifie():
            return redirect(url_for('authentification'))
        if not a_le_role('admin'):
            return render_template('erreur.html', message="Accès refusé : page réservée aux administrateurs."), 403
        return f(*args, **kwargs)
    return verif


# ---------- Catalogue et recherche (F3) ----------
@app.route('/livres')
@connexion_requise
def catalogue():
    q = request.args.get('q', '').strip()
    conn = get_db()
    if q:
        motif = '%' + q + '%'
        livres = conn.execute(SQL_LIVRES_DISPO + ' WHERE livres.titre LIKE ? OR livres.auteur LIKE ? '
                              'GROUP BY livres.id ORDER BY livres.titre', (motif, motif)).fetchall()
    else:
        livres = conn.execute(SQL_LIVRES_DISPO + ' GROUP BY livres.id ORDER BY livres.titre').fetchall()
    conn.close()
    return render_template('livres.html', livres=livres, q=q)


# ---------- Emprunter (F4, R1, R2) ----------
@app.route('/emprunter/<int:livre_id>', methods=['POST'])
@connexion_requise
def emprunter(livre_id):
    user_id = session.get('user_id')
    conn = get_db()
    try:
        livre = conn.execute(SQL_LIVRES_DISPO + ' WHERE livres.id = ? GROUP BY livres.id', (livre_id,)).fetchone()
        if livre is None:
            flash("Livre introuvable.", "erreur")
        elif livre['nb_disponibles'] <= 0:                                    # R1
            flash(f"« {livre['titre']} » n'est plus disponible : tous les exemplaires sont empruntés.", "erreur")
        else:
            nb_en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE utilisateur_id = ? AND date_retour IS NULL',
                                       (user_id,)).fetchone()[0]
            if nb_en_cours >= MAX_EMPRUNTS:                                   # R2
                flash(f"Vous avez déjà {nb_en_cours} livres en cours : {MAX_EMPRUNTS} maximum. Rendez-en un d'abord.", "erreur")
            else:
                conn.execute("INSERT INTO emprunts (livre_id, utilisateur_id, date_retour_prevue) "
                             "VALUES (?, ?, date('now', ?))", (livre_id, user_id, f'+{DUREE_PRET_JOURS} days'))
                conn.commit()
                flash(f"Vous avez emprunté « {livre['titre']} ». À rendre dans {DUREE_PRET_JOURS} jours.", "ok")
    finally:
        conn.close()
    return redirect(request.referrer or url_for('catalogue'))


# ---------- Mes emprunts (F6) ----------
@app.route('/mes_emprunts')
@connexion_requise
def mes_emprunts():
    conn = get_db()
    emprunts = conn.execute('''
        SELECT emprunts.*, livres.titre, livres.auteur,
               (emprunts.date_retour IS NULL AND emprunts.date_retour_prevue < date('now')) AS en_retard
        FROM emprunts
        JOIN livres ON livres.id = emprunts.livre_id
        WHERE emprunts.utilisateur_id = ?
        ORDER BY emprunts.date_retour IS NOT NULL, emprunts.date_emprunt DESC
    ''', (session.get('user_id'),)).fetchall()
    conn.close()
    en_cours = [e for e in emprunts if e['date_retour'] is None]
    historique = [e for e in emprunts if e['date_retour'] is not None]
    nb_retards = sum(1 for e in en_cours if e['en_retard'])
    return render_template('mes_emprunts.html', en_cours=en_cours, historique=historique,
                           nb_retards=nb_retards, max_emprunts=MAX_EMPRUNTS)


# ---------- Rendre (F5) : on ne supprime pas, on remplit date_retour ----------
@app.route('/rendre/<int:emprunt_id>', methods=['POST'])
@connexion_requise
def rendre(emprunt_id):
    conn = get_db()
    try:
        emprunt = conn.execute('SELECT * FROM emprunts WHERE id = ?', (emprunt_id,)).fetchone()
        if emprunt is None or emprunt['date_retour'] is not None:
            flash("Emprunt introuvable ou déjà rendu.", "erreur")
        elif emprunt['utilisateur_id'] != session.get('user_id') and not a_le_role('admin'):
            return render_template('erreur.html', message="Ce n'est pas votre emprunt."), 403
        else:
            conn.execute("UPDATE emprunts SET date_retour = CURRENT_TIMESTAMP WHERE id = ?", (emprunt_id,))
            conn.commit()
            flash("Livre rendu, merci !", "ok")
    finally:
        conn.close()
    return redirect(request.referrer or url_for('mes_emprunts'))


# ---------- Administration des livres (F1, F2, R3, R5) ----------
def lire_formulaire_livre():
    """Récupère et vérifie le formulaire livre. Renvoie (valeurs, erreur)."""
    v = {
        'titre': request.form.get('titre', '').strip(),
        'auteur': request.form.get('auteur', '').strip(),
        'isbn': request.form.get('isbn', '').strip(),
        'annee': request.form.get('annee', '').strip(),
        'genre': request.form.get('genre', '').strip(),
        'nb_exemplaires': request.form.get('nb_exemplaires', '1').strip(),
    }
    if not v['titre'] or not v['auteur']:                                      # R5
        return v, "Le titre et l'auteur sont obligatoires."
    try:
        v['nb_exemplaires'] = int(v['nb_exemplaires'])
        v['annee'] = int(v['annee']) if v['annee'] else None
    except ValueError:
        return v, "L'année et le nombre d'exemplaires doivent être des nombres."
    if v['nb_exemplaires'] < 0:
        return v, "Le nombre d'exemplaires ne peut pas être négatif."
    return v, None


@app.route('/admin/livres')
@admin_requis
def admin_livres():
    conn = get_db()
    livres = conn.execute(SQL_LIVRES_DISPO + ' GROUP BY livres.id ORDER BY livres.titre').fetchall()
    conn.close()
    return render_template('admin_livres.html', livres=livres)


@app.route('/admin/livres/nouveau', methods=['GET', 'POST'])
@admin_requis
def admin_livre_nouveau():
    if request.method == 'POST':
        v, erreur = lire_formulaire_livre()
        if erreur:
            return render_template('livre_form.html', livre=v, erreur=erreur, titre_page="Nouveau livre"), 400
        conn = get_db()
        conn.execute('INSERT INTO livres (titre, auteur, isbn, annee, genre, nb_exemplaires) VALUES (?, ?, ?, ?, ?, ?)',
                     (v['titre'], v['auteur'], v['isbn'], v['annee'], v['genre'], v['nb_exemplaires']))
        conn.commit()
        conn.close()
        flash(f"Livre « {v['titre']} » ajouté.", "ok")
        return redirect(url_for('admin_livres'))
    return render_template('livre_form.html', livre={'nb_exemplaires': 1}, titre_page="Nouveau livre")


@app.route('/admin/livres/<int:id>/modifier', methods=['GET', 'POST'])
@admin_requis
def admin_livre_modifier(id):
    conn = get_db()
    try:
        livre = conn.execute(SQL_LIVRES_DISPO + ' WHERE livres.id = ? GROUP BY livres.id', (id,)).fetchone()
        if livre is None:
            return render_template('erreur.html', message="Livre introuvable."), 404
        if request.method == 'POST':
            v, erreur = lire_formulaire_livre()
            nb_empruntes = livre['nb_exemplaires'] - livre['nb_disponibles']
            if not erreur and v['nb_exemplaires'] < nb_empruntes:
                erreur = f"Impossible : {nb_empruntes} exemplaire(s) sont actuellement empruntés."
            if erreur:
                v['id'] = id
                return render_template('livre_form.html', livre=v, erreur=erreur, titre_page="Modifier un livre"), 400
            conn.execute('UPDATE livres SET titre = ?, auteur = ?, isbn = ?, annee = ?, genre = ?, nb_exemplaires = ? '
                         'WHERE id = ?',
                         (v['titre'], v['auteur'], v['isbn'], v['annee'], v['genre'], v['nb_exemplaires'], id))
            conn.commit()
            flash(f"Livre « {v['titre']} » modifié.", "ok")
            return redirect(url_for('admin_livres'))
        return render_template('livre_form.html', livre=livre, titre_page="Modifier un livre")
    finally:
        conn.close()


@app.route('/admin/livres/<int:id>/supprimer', methods=['POST'])
@admin_requis
def admin_livre_supprimer(id):
    conn = get_db()
    try:
        en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE livre_id = ? AND date_retour IS NULL',
                                (id,)).fetchone()[0]
        if en_cours > 0:                                                       # R3
            flash(f"Suppression impossible : {en_cours} exemplaire(s) en cours d'emprunt.", "erreur")
        else:
            # Les anciens emprunts (rendus) de ce livre sont supprimés avec lui
            conn.execute('DELETE FROM emprunts WHERE livre_id = ?', (id,))
            conn.execute('DELETE FROM livres WHERE id = ?', (id,))
            conn.commit()
            flash("Livre supprimé.", "ok")
    finally:
        conn.close()
    return redirect(url_for('admin_livres'))


# ---------- Administration des utilisateurs (F7) ----------
@app.route('/admin/utilisateurs')
@admin_requis
def admin_utilisateurs():
    conn = get_db()
    utilisateurs = conn.execute('''
        SELECT utilisateurs.id, utilisateurs.login, utilisateurs.nom, utilisateurs.prenom, utilisateurs.role,
               COUNT(emprunts.id) AS nb_en_cours
        FROM utilisateurs
        LEFT JOIN emprunts ON emprunts.utilisateur_id = utilisateurs.id AND emprunts.date_retour IS NULL
        GROUP BY utilisateurs.id
        ORDER BY utilisateurs.role, utilisateurs.login
    ''').fetchall()
    conn.close()
    return render_template('admin_utilisateurs.html', utilisateurs=utilisateurs)


@app.route('/admin/utilisateurs/nouveau', methods=['GET', 'POST'])
@admin_requis
def admin_utilisateur_nouveau():
    if request.method == 'POST':
        v = {k: request.form.get(k, '').strip() for k in ('login', 'nom', 'prenom', 'mot_de_passe', 'role')}
        if not v['login'] or not v['mot_de_passe'] or v['role'] not in ('admin', 'user'):
            return render_template('utilisateur_form.html', u=v,
                                   erreur="Login, mot de passe et rôle sont obligatoires."), 400
        conn = get_db()
        try:
            conn.execute('INSERT INTO utilisateurs (login, nom, prenom, mot_de_passe_hash, role) VALUES (?, ?, ?, ?, ?)',
                         (v['login'], v['nom'], v['prenom'], generate_password_hash(v['mot_de_passe']), v['role']))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('utilisateur_form.html', u=v, erreur="Ce login existe déjà."), 400
        finally:
            conn.close()
        flash(f"Compte « {v['login']} » créé.", "ok")
        return redirect(url_for('admin_utilisateurs'))
    return render_template('utilisateur_form.html', u={'role': 'user'})


@app.route('/admin/utilisateurs/<int:id>/supprimer', methods=['POST'])
@admin_requis
def admin_utilisateur_supprimer(id):
    if id == session.get('user_id'):
        flash("Vous ne pouvez pas supprimer votre propre compte.", "erreur")
        return redirect(url_for('admin_utilisateurs'))
    conn = get_db()
    try:
        en_cours = conn.execute('SELECT COUNT(*) FROM emprunts WHERE utilisateur_id = ? AND date_retour IS NULL',
                                (id,)).fetchone()[0]
        if en_cours > 0:
            flash(f"Suppression impossible : cet utilisateur a {en_cours} livre(s) à rendre.", "erreur")
        else:
            conn.execute('DELETE FROM emprunts WHERE utilisateur_id = ?', (id,))
            conn.execute('DELETE FROM utilisateurs WHERE id = ?', (id,))
            conn.commit()
            flash("Utilisateur supprimé.", "ok")
    finally:
        conn.close()
    return redirect(url_for('admin_utilisateurs'))


# ---------- Bonus : tous les emprunts en cours + retards ----------
@app.route('/admin/emprunts')
@admin_requis
def admin_emprunts():
    conn = get_db()
    emprunts = conn.execute('''
        SELECT emprunts.*, livres.titre, utilisateurs.login,
               (emprunts.date_retour_prevue < date('now')) AS en_retard
        FROM emprunts
        JOIN livres ON livres.id = emprunts.livre_id
        JOIN utilisateurs ON utilisateurs.id = emprunts.utilisateur_id
        WHERE emprunts.date_retour IS NULL
        ORDER BY emprunts.date_retour_prevue
    ''').fetchall()
    conn.close()
    return render_template('admin_emprunts.html', emprunts=emprunts)


# ---------- Bonus : statistiques ----------
@app.route('/admin/stats')
@admin_requis
def admin_stats():
    conn = get_db()
    top = conn.execute('''
        SELECT livres.titre, livres.auteur, COUNT(emprunts.id) AS nb
        FROM livres JOIN emprunts ON emprunts.livre_id = livres.id
        GROUP BY livres.id ORDER BY nb DESC, livres.titre LIMIT 5
    ''').fetchall()
    genres = conn.execute('''
        SELECT COALESCE(livres.genre, '?') AS genre, COUNT(emprunts.id) AS nb
        FROM emprunts JOIN livres ON livres.id = emprunts.livre_id
        GROUP BY livres.genre ORDER BY nb DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_stats.html', top=top, genres=genres)


# ---------- API JSON (F9) ----------
@app.get('/api/livres')
def api_livres():
    q = request.args.get('q', '').strip()
    conn = get_db()
    if q:
        motif = '%' + q + '%'
        rows = conn.execute(SQL_LIVRES_DISPO + ' WHERE livres.titre LIKE ? OR livres.auteur LIKE ? '
                            'GROUP BY livres.id ORDER BY livres.titre', (motif, motif)).fetchall()
    else:
        rows = conn.execute(SQL_LIVRES_DISPO + ' GROUP BY livres.id ORDER BY livres.titre').fetchall()
    conn.close()
    return jsonify([dict(r, disponible=r['nb_disponibles'] > 0) for r in rows])


@app.get('/api/livres/<int:id>')
def api_livre(id):
    conn = get_db()
    r = conn.execute(SQL_LIVRES_DISPO + ' WHERE livres.id = ? GROUP BY livres.id', (id,)).fetchone()
    conn.close()
    if r is None:
        return jsonify({'erreur': 'Livre introuvable'}), 404
    return jsonify(dict(r, disponible=r['nb_disponibles'] > 0))


# ---------------------------------------------------------------
#  Ne pas modifier : utile seulement pour lancer le site
#  sur votre propre ordinateur (python flask_app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)