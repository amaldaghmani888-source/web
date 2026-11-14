# Carnet de santé de la femme — version avec accès par rôle

## Installation
1. Python 3.10+ recommandé.
2. `python -m venv .venv` puis activer l'environnement.
3. `pip install -r requirements.txt`
4. `python app.py`
5. Ouvrir `http://127.0.0.1:5000`.

## Accès
- **Femme :** saisie du CIN uniquement, sans mot de passe. À la première connexion, le dossier d'accès est créé automatiquement.
- **Personnel de santé :** créer un compte avec nom, prénom et mot de passe (8 caractères minimum). L'identifiant est généré sous la forme `nomprenom@sante`. Ensuite, se connecter avec cet identifiant et le mot de passe.
- **Espace femme :** seules les rubriques « Mes rendez-vous » et « Historique » sont affichées.
- **Espace professionnel :** tableau d'indicateurs, graphique des volumes enregistrés et formulaires de saisie. Pour rattacher une saisie à l'historique d'une femme, le professionnel indique son CIN.

## Limites importantes avant usage réel
Cette livraison est une version de démonstration fonctionnelle, pas un système médical prêt pour la production. Le CIN seul n'est pas un facteur d'authentification suffisamment sûr : toute personne connaissant le CIN pourrait ouvrir l'espace correspondant. Il faut mettre en place une vérification d'identité/OTP ou un code secret remis de manière sécurisée. La création libre de comptes professionnels doit également être remplacée par une validation administrative. Avant tout usage avec de vraies données de santé, ajouter HTTPS, protection CSRF, limitation des tentatives, journal d'audit, sauvegardes chiffrées, contrôle d'accès renforcé, gestion des consentements et validation juridique/réglementaire au Maroc.
