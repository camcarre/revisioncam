#!/bin/bash

# Script de build pour Render
echo "🚀 Démarrage du build RevisionCam..."

# Mettre à jour pip
echo "📦 Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier que uvicorn est installé
echo "🔍 Vérification de uvicorn..."
python -c "import uvicorn; print('✅ uvicorn installé avec succès')"

# Vérifier que l'application peut être importée
echo "🔍 Vérification de l'application..."
python -c "from app.main import app; print('✅ Application importée avec succès')"

echo "✅ Build terminé avec succès !"
