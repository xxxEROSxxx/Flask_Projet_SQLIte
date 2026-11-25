-- Migration 001 : ajout du téléphone (à exécuter UNE SEULE FOIS sur chaque serveur)
ALTER TABLE clients ADD COLUMN telephone TEXT;
