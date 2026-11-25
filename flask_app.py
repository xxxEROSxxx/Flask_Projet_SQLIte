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

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
    return render_template('hello.html')


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
            return redirect(url_for('lecture'))
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


# ---------------------------------------------------------------
#  Ne pas modifier : utile seulement pour lancer le site
#  sur votre propre ordinateur (python flask_app.py)
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)