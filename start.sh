#!/bin/bash
echo "🚀 Démarrage de RevisionCam sur Render..."
echo "📋 Installation des dépendances..."
pip install -r requirements.txt

echo "📊 Initialisation des données..."
python3 -c "
import json
import os
from datetime import datetime

# Créer les données par défaut si le fichier n'existe pas
if not os.path.exists('revisioncam.json'):
    default_data = {
        'examens': [],
        'cours': [],
        'planning': [],
        'scores': [],
        'parametres': [
            {'cle': 'duree_min', 'valeur': 30},
            {'cle': 'duree_max', 'valeur': 90},
            {'cle': 'nb_max_par_j', 'valeur': 4},
            {'cle': 'nb_min_par_j', 'valeur': 1},
            {'cle': 'bonus_ok', 'valeur': 2},
            {'cle': 'bonus_fail', 'valeur': 1},
            {'cle': 'seuil_ok', 'valeur': 85},
            {'cle': 'seuil_fail', 'valeur': 60},
            {'cle': 'temps_pause', 'valeur': 15}
        ],
        'bareme': [
            {'indice': i, 'nb_revisions': i+1} for i in range(11)
        ],
        'disponibilites': [
            {'jour': 'lundi', 'minutes': 480},
            {'jour': 'mardi', 'minutes': 480},
            {'jour': 'mercredi', 'minutes': 480},
            {'jour': 'jeudi', 'minutes': 480},
            {'jour': 'vendredi', 'minutes': 480},
            {'jour': 'samedi', 'minutes': 360},
            {'jour': 'dimanche', 'minutes': 240}
        ],
        'planning_logs': []
    }
    
    with open('revisioncam.json', 'w') as f:
        json.dump(default_data, f, indent=2)
    
    print('✅ Fichier revisioncam.json créé avec les données par défaut')

print('✅ Données initialisées')
"

echo "🌐 Démarrage du serveur..."
gunicorn app_flask_json:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
