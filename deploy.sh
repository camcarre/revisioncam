#!/bin/bash

# Script de déploiement pour RevisionCam
# Ce script prépare et pousse le code sur GitHub

echo "🚀 Déploiement de RevisionCam vers GitHub"
echo "========================================"

# Vérifier que git est initialisé
if [ ! -d ".git" ]; then
    echo "📁 Initialisation du repository Git..."
    git init
    git remote add origin https://github.com/camcarre/revisioncam.git
fi

# Ajouter tous les fichiers
echo "📦 Ajout des fichiers..."
git add .

# Commit avec message
echo "💾 Création du commit..."
git commit -m "🚀 Déploiement initial de RevisionCam

✨ Fonctionnalités:
- Interface Apple-style moderne
- Planning de révisions adaptatif
- Module CardCamille intégré
- Système d'authentification simple
- API FastAPI complète
- Base de données SQLite
- Interface responsive
- Protection par mot de passe

🎯 Prêt pour le déploiement sur Render"

# Pousser vers GitHub
echo "🌐 Poussée vers GitHub..."
git branch -M main
git push -u origin main

echo "✅ Déploiement terminé !"
echo "🌐 Votre code est maintenant disponible sur: https://github.com/camcarre/revisioncam"
echo ""
echo "📋 Prochaines étapes pour Render:"
echo "1. Aller sur https://render.com"
echo "2. Créer un nouveau Web Service"
echo "3. Connecter le repository revisioncam"
echo "4. Configurer avec les paramètres du README"
echo "5. Déployer !"
