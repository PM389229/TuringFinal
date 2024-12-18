# Plateforme de Turing

Ce projet est une plateforme éducative conçue pour faciliter l'enseignement et l'apprentissage du test de Turing à travers un quizz interactif .
La plateforme utilise Flask comme framework backend, MySQL pour la gestion de la base de données, et Hugging Face pour la génération du contenu de texte.

## Fonctionnalités

- **Authentification** : Connexion et inscription pour les utilisateurs.
- **Rôles Utilisateurs** : Différenciation entre formateurs et élèves avec des interfaces et des fonctionnalités spécifiques.
- **Gestion des Thèmes** : Les formateurs peuvent ajouter des thèmes et générer des phrases via une intégration avec Hugging Face.
- **Quizz** : Les élèves peuvent participer à des quizz basés sur les thèmes et phrases générés.

## Prérequis

- Python 3.8+
- MySQL Server
- Docker (optionnel pour l'environnement de conteneurisation)
