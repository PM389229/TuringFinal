# Utiliser une image de base Python légère
FROM python:3.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet dans le répertoire de travail du conteneur
COPY . /app

# Installer les dépendances nécessaires à partir du fichier requirements.txt
RUN pip install -r requirements.txt

# Exposer le port sur lequel Flask s'exécute
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["flask", "run", "--host=0.0.0.0"]
