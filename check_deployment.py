#!/usr/bin/env python3
"""
Script de vérification pour le déploiement
Vérifie que tous les fichiers nécessaires sont présents
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MANQUANT")
        return False

def check_directory_exists(dirpath, description):
    """Vérifie qu'un dossier existe"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - MANQUANT")
        return False

def main():
    print("🔍 Vérification du déploiement RevisionCam")
    print("=" * 50)
    
    checks = []
    
    # Fichiers essentiels
    checks.append(check_file_exists("requirements.txt", "Requirements"))
    checks.append(check_file_exists("Procfile", "Procfile"))
    checks.append(check_file_exists("render.yaml", "Configuration Render"))
    checks.append(check_file_exists(".gitignore", "Git ignore"))
    checks.append(check_file_exists("README.md", "Documentation"))
    checks.append(check_file_exists("deploy.sh", "Script de déploiement"))
    
    # Structure de l'application
    checks.append(check_directory_exists("app", "Dossier application"))
    checks.append(check_file_exists("app/main.py", "Point d'entrée FastAPI"))
    checks.append(check_file_exists("app/database.py", "Configuration base de données"))
    checks.append(check_file_exists("app/models.py", "Modèles SQLAlchemy"))
    checks.append(check_file_exists("app/initial_data.py", "Données initiales"))
    
    # Frontend
    checks.append(check_directory_exists("frontend", "Dossier frontend"))
    checks.append(check_file_exists("frontend/index.html", "Page d'accueil"))
    checks.append(check_file_exists("frontend/cours.html", "Page cours"))
    checks.append(check_file_exists("frontend/planning.html", "Page planning"))
    checks.append(check_file_exists("frontend/parametres.html", "Page paramètres"))
    checks.append(check_file_exists("frontend/scores.html", "Page scores"))
    
    # CardCamille
    checks.append(check_directory_exists("frontend/cardcamille", "Dossier CardCamille"))
    checks.append(check_file_exists("frontend/cardcamille/index.html", "CardCamille - Cartes"))
    checks.append(check_file_exists("frontend/cardcamille/qcm.html", "CardCamille - QCM"))
    checks.append(check_file_exists("frontend/cardcamille/style.css", "CSS CardCamille"))
    checks.append(check_file_exists("frontend/cardcamille/app.js", "JavaScript cartes"))
    checks.append(check_file_exists("frontend/cardcamille/qcm.js", "JavaScript QCM"))
    
    # Fichiers d'exemple
    checks.append(check_file_exists("frontend/cardcamille/exemple_cartes.csv", "Exemple cartes CSV"))
    checks.append(check_file_exists("frontend/cardcamille/exemple_qcm.csv", "Exemple QCM CSV"))
    
    # Résumé
    print("\n" + "=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    print(f"📊 Résultat: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("🎉 Tous les fichiers sont présents ! Prêt pour le déploiement.")
        print("\n🚀 Pour déployer:")
        print("1. Exécuter: ./deploy.sh")
        print("2. Aller sur https://render.com")
        print("3. Créer un Web Service avec ce repository")
        return True
    else:
        print("⚠️ Certains fichiers manquent. Vérifiez avant le déploiement.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
