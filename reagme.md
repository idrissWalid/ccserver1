📱 API de Paiement Mobile - Flask
Une API Flask simple pour gérer les abonnements via des notifications de paiement mobile. L'API extrait automatiquement les numéros de téléphone des messages de transaction et gère l'état d'abonnement des utilisateurs.

🚀 Fonctionnalités
Extraction automatique des numéros de téléphone depuis les messages de paiement

Gestion d'abonnement : création, activation, vérification et désabonnement

Base de données SQLite intégrée avec SQLAlchemy

API RESTful avec endpoints clairs

Support JSON et texte brut pour les requêtes

🗄️ Structure de la Base de Données
Table User
Champ	Type	Description
id	Integer	Clé primaire
phone_number	String(8)	Numéro de téléphone (8 chiffres) - UNIQUE
issubscribed	Boolean	État d'abonnement (False par défaut)
subscribe_date	DateTime	Date d'abonnement (quand issubscribed=True)
🛠️ Installation
Prérequis
Python 3.7+

pip (gestionnaire de paquets Python)

Étapes d'installation
Cloner ou créer le projet

bash
mkdir api-paiement-mobile
cd api-paiement-mobile
Créer un environnement virtuel (optionnel mais recommandé)

bash
python -m venv venv
# Sur Windows:
venv\Scripts\activate
# Sur Mac/Linux:
source venv/bin/activate
Installer les dépendances

bash
pip install flask flask-sqlalchemy
Créer le fichier app.py
Copier le code fourni dans un fichier nommé app.py

Lancer l'application

bash
python app.py
Le serveur démarre sur http://localhost:5000

📊 Endpoints API
1. POST /api/subscribe - Gérer un abonnement
Traite un message de paiement et gère l'abonnement de l'utilisateur.

Format du message attendu:

text
"Vous avez recu 500.00 FCFA du 65956557,ABDOULAYE. Le solde de votre compte est de 1038.81 FCFA Trans ID: PP260130.2010.95785245."
Scénarios:

Si le numéro n'existe pas → Crée un nouvel utilisateur avec issubscribed=True

Si le numéro existe avec issubscribed=False → Passe à True et met à jour subscribe_date

Si le numéro existe avec issubscribed=True → Retourne "déjà abonné"

Requêtes:

Avec JSON:

bash
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Vous avez recu 500.00 FCFA du 65956557,ABDOULAYE. Le solde de votre compte est de 1038.81 FCFA"
  }'
Avec texte brut:

bash
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: text/plain" \
  -d "Vous avez recu 500.00 FCFA du 12345678,ABDOULAYE. Le solde de votre compte est de 1038.81 FCFA"
Réponses possibles:

Nouvel utilisateur créé (201):

json
{
  "phone_number": "65956557",
  "action": "created",
  "issubscribed": true,
  "subscribe_date": "2024-01-30T10:30:00.000000"
}
Utilisateur mis à jour (200):

json
{
  "phone_number": "65956557",
  "action": "updated",
  "issubscribed": true,
  "subscribe_date": "2024-01-30T10:30:00.000000"
}
Déjà abonné (200):

json
{
  "phone_number": "65956557",
  "action": "already_subscribed",
  "issubscribed": true,
  "subscribe_date": "2024-01-30T10:30:00.000000"
}
2. GET /api/check/<phone_number> - Vérifier un abonnement
Vérifie si un utilisateur existe et son état d'abonnement.

Requête:

bash
curl http://localhost:5000/api/check/65956557
Réponses:

Utilisateur trouvé et abonné (200):

json
{
  "phone_number": "65956557",
  "exists": true,
  "issubscribed": true,
  "subscribe_date": "2024-01-30T10:30:00.000000"
}
Utilisateur trouvé mais non abonné (200):

json
{
  "phone_number": "65956557",
  "exists": true,
  "issubscribed": false,
  "subscribe_date": null
}
Utilisateur non trouvé (404):

json
{
  "phone_number": "65956557",
  "exists": false,
  "issubscribed": false,
  "message": "Utilisateur non trouvé"
}
3. POST /api/unsubscribe/<phone_number> - Désabonner
Désabonne un utilisateur.

Requête:

bash
curl -X POST http://localhost:5000/api/unsubscribe/65956557
Réponse (200):

json
{
  "phone_number": "65956557",
  "issubscribed": false,
  "message": "Désabonnement réussi"
}
4. GET /api/users - Lister tous les utilisateurs
Récupère la liste de tous les utilisateurs (pour administration).

Requête:

bash
curl http://localhost:5000/api/users
Réponse (200):

json
{
  "total": 2,
  "users": [
    {
      "phone_number": "65956557",
      "issubscribed": true,
      "subscribe_date": "2024-01-30T10:30:00.000000"
    },
    {
      "phone_number": "12345678",
      "issubscribed": false,
      "subscribe_date": null
    }
  ]
}
🔧 Tests Complets
Scénario 1: Nouvel abonnement
bash
# 1. Envoyer un message de paiement pour un nouveau numéro
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"message": "Vous avez recu 500.00 FCFA du 77123456,MOHAMED. Le solde de votre compte est de 1500.00 FCFA"}'

# 2. Vérifier l'abonnement
curl http://localhost:5000/api/check/77123456
Scénario 2: Réabonnement
bash
# 1. Désabonner d'abord
curl -X POST http://localhost:5000/api/unsubscribe/77123456

# 2. Réabonner via un nouveau paiement
curl -X POST http://localhost:5000/api/subscribe \
  -H "Content-Type: text/plain" \
  -d "Vous avez recu 1000.00 FCFA du 77123456,MOHAMED. Le solde de votre compte est de 2500.00 FCFA"
⚠️ Codes d'Erreur
Code	Description
400	Requête invalide (message vide, format incorrect)
404	Ressource non trouvée (utilisateur inexistant)
500	Erreur serveur interne
🗂️ Fichiers du Projet
text
api-paiement-mobile/
├── app.py              # Application Flask principale
├── payments.db         # Base de données SQLite (créée automatiquement)
└── README.md          # Ce fichier
🔍 Notes Techniques
Extraction des numéros
L'API recherche une séquence de 8 chiffres consécutifs dans le message

Format attendu: \d{8} (ex: 65956557, 12345678)

Le numéro doit être présent dans le message pour être extrait

Gestion des dates
subscribe_date est automatiquement mis à jour lors de l'abonnement

Format: ISO 8601 (ex: "2024-01-30T10:30:00.000000")

La date est définie sur null lors du désabonnement

Validation
Tous les numéros sont validés (8 chiffres exactement)

Support des requêtes JSON et texte brut pour /api/subscribe

Gestion des doublons (numéro unique dans la base)

🚀 Déploiement
Pour un environnement de production:

Désactiver le mode debug:

python
if __name__ == '__main__':
    app.run(debug=False, port=5000)
Utiliser un serveur WSGI comme Gunicorn:

bash
pip install gunicorn
gunicorn -w 4 app:app
Configurer un reverse proxy (Nginx/Apache) pour la sécurité et la performance

📞 Support
Pour toute question ou problème:

Vérifier que le numéro contient exactement 8 chiffres

S'assurer que le message contient bien le numéro

Vérifier que la base de données (payments.db) est accessible en écriture

Consulter les logs du serveur Flask pour les erreurs détaillées