# 📒 Mon carnet de bord

**Nom :** RIGUIDEL

**Prénom :** Eros-Nathan

**Adresse de mon site :** https://marabout.pythonanywhere.com

**Adresse de mon dépôt GitHub :** https://github.com/xxxEROSxxx/Flask_Projet_SQLIte

> Modifiez ce fichier directement sur GitHub (icône crayon ✏️) pour répondre aux questions de chaque exercice.
> Écrivez avec vos propres mots : une réponse courte et juste vaut mieux qu'un long copier-coller ! 🙂

---

## 🟢 Exercice 1 — Explorer la base en SQL

1. Expliquez avec vos mots la différence entre une **table**, une **colonne** et une **ligne**.

   > _Ma réponse :_ La table c'est le tableau des clients. Une colonne c'est une info (nom, prénom…). Une ligne c'est un client.

2. À quoi sert la clé primaire `id` ? Pourquoi ne pas simplement identifier un client par son nom ?

   > _Ma réponse :_ L'id c'est un numéro unique pour chaque client. Le nom ne suffit pas car deux personnes peuvent avoir le même.

3. Pourquoi votre client ajouté en console est-il apparu sur le site ?

   > _Ma réponse :_ Parce que le site lit la base à chaque fois qu'on ouvre la page. Pas besoin de toucher au code.

4. Que signifie `NOT NULL` dans `schema.sql` ? Quelle erreur avez-vous obtenue avec `INSERT INTO clients (nom) VALUES ('TEST');` ?

   > _Ma réponse :_ Ça veut dire que la case est obligatoire. Erreur : `NOT NULL constraint failed: clients.prenom`, il manquait le prénom.

🧩 **Défi** — mes requêtes / ma solution :

   > `SELECT * FROM clients ORDER BY id DESC LIMIT 3;`
   > `SELECT * FROM clients WHERE prenom LIKE 'A%';`
   > `SELECT COUNT(*) FROM clients WHERE adresse LIKE '%Paris%';`

---

## 🟢 Exercice 2 — Afficher les données proprement

1. Décrivez avec vos mots le trajet d'une requête, du navigateur jusqu'à la base de données, puis le retour.

   > _Ma réponse :_ Le navigateur demande la page à Flask. Flask demande les clients à la base. La base répond. Flask fait la page HTML et la renvoie au navigateur.

2. Pourquoi faut-il **fermer** la connexion (`conn.close()`) après chaque requête ?

   > _Ma réponse :_ Pour libérer la base. Sinon elle peut rester bloquée.

3. Quel est l'avantage d'écrire `row['nom']` plutôt que `row[2]` ? (Pensez à ce qui arriverait si on ajoutait une colonne au milieu de la table.)

   > _Ma réponse :_ C'est plus clair. Et si on ajoute une colonne au milieu, `row[2]` affichera la mauvaise info, pas `row['nom']`.

4. Pourquoi est-il préférable de trier avec `ORDER BY` dans la requête SQL plutôt qu'en Python ?

   > _Ma réponse :_ La base trie plus vite, et ça fait moins de code en Python.

🧩 **Défi** — mes requêtes / ma solution :

   > J'ai fait une page `fiche_client.html` pour un seul client, avec `fetchone()`, et un message "Client introuvable" si l'id n'existe pas.

---

## 🟢 Exercice 3 — Rechercher un client

1. Quelle est la différence entre `WHERE nom = 'DUPONT'` et `WHERE nom LIKE '%DUP%'` ?

   > _Ma réponse :_ Avec `=` il faut le nom exact. Avec `LIKE '%DUP%'` ça trouve tous les noms qui contiennent "DUP".

2. Expliquez avec vos mots ce qu'est une **injection SQL**. Qu'est-ce qu'un pirate pourrait faire de pire qu'afficher tous les clients ?

   > _Ma réponse :_ C'est quand un pirate tape du SQL dans un champ et que le site l'exécute. Il pourrait supprimer toute la base ou voler des données.

3. Pourquoi la version avec `?` est-elle protégée contre l'injection ?

   > _Ma réponse :_ Avec le `?`, ce que tape l'utilisateur est lu comme du texte, jamais comme du code.

4. Pour la recherche, on a utilisé `method="get"`. Quel avantage pour l'utilisateur ? (Indice : favoris, partage de lien.)

   > _Ma réponse :_ La recherche est dans l'URL, donc on peut la mettre en favori ou l'envoyer à quelqu'un.

🧩 **Défi** — mes requêtes / ma solution :

   > Une liste déroulante pour choisir le tri. En Python, on accepte seulement `nom`, `prenom` ou `created`, sinon on trie par nom.

---

## 🔵 Exercice 4 — Enregistrer un client

1. Quelles étaient les deux anomalies du formulaire d'origine, et d'où venaient-elles ?

   > _Ma réponse :_ La date était un faux nombre (`1002938`) et l'adresse était toujours "ICI". Les deux étaient écrits en dur dans le code.

2. Pourquoi la validation côté **navigateur** (`required`) ne suffit-elle pas ? Pourquoi la garder quand même ?

   > _Ma réponse :_ N'importe qui peut enlever le `required` avec F12. On le garde quand même car c'est pratique pour l'utilisateur.

3. À quoi sert `conn.commit()` ? Que se passe-t-il sans lui ?

   > _Ma réponse :_ `commit()` sauvegarde vraiment dans la base. Sans lui, le client n'est pas enregistré.

4. Pourquoi redirige-t-on vers `/consultation/` après l'enregistrement, au lieu d'afficher directement une page ? (Indice : essayez d'appuyer sur F5 après l'envoi.)

   > _Ma réponse :_ Sinon un F5 renverrait le formulaire et créerait le client en double.

---

## 🔵 Exercice 5 — Modifier et supprimer

1. Que signifie CRUD ? Donnez la requête SQL correspondant à chaque lettre.

   > _Ma réponse :_ Créer = `INSERT`, Lire = `SELECT`, Modifier = `UPDATE`, Supprimer = `DELETE`.

2. Que se passe-t-il si l'on oublie le `WHERE` dans un `UPDATE` ou un `DELETE` ? À quoi servent `BEGIN` et `ROLLBACK` ?

   > _Ma réponse :_ Sans `WHERE`, ça touche toute la table. `BEGIN` commence un essai et `ROLLBACK` l'annule, comme un Ctrl+Z.

3. Pourquoi ne faut-il **jamais** supprimer des données avec une requête GET (un simple lien) ? (Indice : les moteurs de recherche et certains navigateurs « visitent » les liens à l'avance.)

   > _Ma réponse :_ Des robots ou navigateurs cliquent sur les liens tout seuls. Ils pourraient supprimer des clients sans le vouloir.

4. Une fois un `id` supprimé, pourquoi est-il préférable qu'il ne soit jamais réattribué à un autre client ?

   > _Ma réponse :_ Sinon un nouveau client récupérerait les anciennes infos liées à cet id.

---

## 🟣 Exercice 6 — Faire évoluer la base

1. Quelle est la différence entre le **schéma** d'une base et ses **données** ? Où se trouve chacun ?

   > _Ma réponse :_ Le schéma c'est la structure (tables, colonnes), dans `schema.sql` sur GitHub. Les données c'est les clients, dans `database.db` sur le serveur.

2. Pourquoi ne faut-il pas relancer `create_db.py` sur une application en production ?

   > _Ma réponse :_ Parce qu'il efface la table et la recrée vide. On perdrait tous les clients.

3. Pourquoi est-il important de garder `schema.sql` à jour, même si on a modifié la base avec `ALTER TABLE` ?

   > _Ma réponse :_ Pour que le fichier corresponde à la vraie base si on doit la recréer un jour.

4. Pour ajouter **une** information, combien de fichiers avez-vous dû modifier ? Lesquels ?

   > _Ma réponse :_ Plusieurs : la base, `schema.sql`, `formulaire.html`, `read_data.html`, `modifier_client.html` et `flask_app.py`.

---

## 🟣 Exercice 7 — Relier deux tables

1. Qu'est-ce qu'une **clé étrangère** ? Dans quelle table se trouve-t-elle ici, et pourquoi pas dans l'autre ?

   > _Ma réponse :_ C'est une colonne qui pointe vers l'id d'une autre table. Ici `client_id` dans `commandes`, car une commande appartient à un seul client.

2. Pourquoi est-ce une mauvaise idée de créer des colonnes `commande1`, `commande2`… dans la table `clients` ?

   > _Ma réponse :_ On ne sait pas combien de commandes il y aura, et plein de cases resteraient vides.

3. À quoi sert un `JOIN` ? Et un `GROUP BY` ?

   > _Ma réponse :_ `JOIN` relie deux tables. `GROUP BY` regroupe les lignes pour compter ou faire des totaux.

4. Pour la bibliothèque, quelles tables imaginez-vous ? Lesquelles contiendront des clés étrangères ?

   > _Ma réponse :_ `livres`, `utilisateurs` et `emprunts`. C'est `emprunts` qui aura les clés étrangères.

---

## 🔴 Exercice 8 — Contrôle d'accès

1. Quelle est la différence entre **authentification** et **autorisation** ?

   > _Ma réponse :_ Authentification = prouver qui on est. Autorisation = ce qu'on a le droit de faire.

2. Où est stockée la session ? Comment le serveur sait-il qui vous êtes à chaque nouvelle requête ?

   > _Ma réponse :_ Dans un cookie du navigateur. Il est renvoyé au serveur à chaque page.

3. Pourquoi masquer un bouton dans le HTML ne suffit-il pas à protéger une action ?

   > _Ma réponse :_ Quelqu'un peut quand même envoyer la requête avec F12. La protection doit être côté serveur.

4. Que signifient les codes `302` et `403` ? Dans quel cas votre application renvoie-t-elle chacun d'eux ?

   > _Ma réponse :_ `302` = redirection (vers la connexion si pas connecté). `403` = interdit (un user qui veut supprimer).

5. Le mot de passe `password` est écrit en clair dans `flask_app.py`, sur un dépôt **public**. Quel est le risque ? Quelle solution avez-vous déjà rencontrée dans cet atelier pour cacher une information sensible ?

   > _Ma réponse :_ Tout le monde peut lire le mot de passe sur GitHub. Solution : les secrets, comme pour le jeton PythonAnywhere.

---

## 🔴 Exercice 9 — Créer une API

1. Quelle est la différence entre une page HTML et une réponse JSON ? À qui chacune est-elle destinée ?

   > _Ma réponse :_ Le HTML c'est pour un humain dans un navigateur. Le JSON c'est des données brutes pour un programme.

2. Que signifient les codes `200`, `201`, `400`, `401` et `404` renvoyés par votre API ?

   > _Ma réponse :_ `200` OK, `201` créé, `400` il manque une info, `401` pas connecté, `404` introuvable.

3. Pourquoi une API renvoie-t-elle une erreur JSON plutôt qu'une redirection vers la page de connexion ?

   > _Ma réponse :_ Parce qu'en face c'est un programme, il ne peut pas remplir un formulaire de connexion.

4. Citez une application de votre téléphone qui, selon vous, utilise une API. Quelles données échange-t-elle ?

   > _Ma réponse :_ Une appli météo : elle envoie ma position et reçoit la température.

---

## 📚 Projet bibliothèque

1. Pourquoi ne supprime-t-on pas un emprunt quand le livre est rendu ?

   > _Ma réponse :_ Pour garder l'historique de qui a emprunté quoi. On met juste une date de retour.

2. Pourquoi calculer la disponibilité d'un livre plutôt que de la stocker dans une colonne ?

   > _Ma réponse :_ Si on la calcule, elle est toujours juste. Une colonne peut être oubliée et devenir fausse.

3. Quelle a été la plus grande difficulté rencontrée pendant le projet, et comment l'avez-vous surmontée ?

   > _Ma réponse :_ Relier les tables avec les bonnes jointures. J'ai testé mes requêtes dans sqlite3 avant de les mettre dans le code.

4. Quelles fonctionnalités n'avez-vous pas eu le temps de réaliser ? Comment vous y prendriez-vous ?

   > _Ma réponse :_ Les alertes de retard. Je comparerais la date d'emprunt avec la date du jour.

---

## 🏁 Pour conclure

En quelques phrases, expliquez à un ami ce qui se passe entre le moment où il clique sur « Enregistrer » dans un formulaire et celui où l'information s'affiche dans une liste :

> _Ma réponse :_ Le navigateur envoie le formulaire à Flask. Flask fait un `INSERT` dans la base. Puis il renvoie vers la liste, qui fait un `SELECT` et affiche la nouvelle ligne.