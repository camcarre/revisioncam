# 📄 RevisionCam - Système JSON

## 🎯 **TRANSFORMATION COMPLÈTE SQLITE → JSON**

RevisionCam a été entièrement transformé pour utiliser un **fichier JSON unique** au lieu de SQLite, rendant l'application **100% portable** et **sans dépendance de base de données**.

---

## 🚀 **AVANTAGES DU NOUVEAU SYSTÈME**

### ✅ **Portabilité totale**
- **Un seul fichier** : `revisioncam.json` contient toutes les données
- **Pas de SQLite** : Plus de problèmes d'installation ou de compatibilité
- **Transportable** : Copiez le fichier JSON sur n'importe quel appareil
- **Hébergement simplifié** : Fonctionne sur tous les hébergeurs gratuits

### ✅ **Facilité d'utilisation**
- **Export/Import** : Sauvegardez et restaurez vos données en un clic
- **Backup automatique** : Le fichier JSON est votre sauvegarde
- **Transparence** : Vous voyez exactement ce qui est stocké
- **Debugging facile** : Ouvrez le JSON dans n'importe quel éditeur

### ✅ **Performance optimisée**
- **Chargement rapide** : Données en mémoire
- **Pas de requêtes SQL** : Accès direct aux données
- **Thread-safe** : Gestion sécurisée des accès concurrents

---

## 🛠️ **INSTALLATION ET UTILISATION**

### **1. Prérequis**
- Python 3.11+
- pip

### **2. Installation**
   ```bash
# Installer les dépendances
   pip install -r requirements.txt
   ```

### **3. Lancement de l'application**
```bash
# Utiliser la version JSON
python app_flask_json.py
```

### **4. Accès à l'application**
- **URL** : http://localhost:8080
- **Identifiants** : `camcam` / `202122`

---

## 📱 **Interface utilisateur**

### Pages principales
- **🏠 Accueil** (`/index.html`) - Tableau de bord principal
- **📚 Cours** (`/cours.html`) - Gestion des cours et examens
- **📅 Planning** (`/planning.html`) - Vue calendrier des révisions
- **📊 Scores** (`/scores.html`) - Enregistrement des résultats QCM
- **⚙️ Paramètres** (`/parametres.html`) - Configuration complète
- **❓ QCM** (`/qcm.html`) - QCM interactifs
- **🃏 CardCamille** (`/indexcardcamille.html`) - Cartes de révision

### 🎨 Design
- Interface style Apple moderne avec Bootstrap
- Responsive design (mobile, tablette, desktop)
- Navigation uniforme sur toutes les pages
- Système d'authentification intégré

---

## 🧠 **Fonctionnalités principales**

### Planning adaptatif
- **Génération automatique** : Création de planning basée sur les cours et priorités
- **Ajustement dynamique** : Modification automatique selon les scores QCM
- **Gestion des disponibilités** : Configuration des créneaux par jour de la semaine
- **Priorisation intelligente** : Les cours majeurs conservent leur planning initial

### CardCamille
- **📝 Cartes de révision** : Import CSV avec retournement 3D
- **❓ QCM interactifs** : Questions à choix multiples avec feedback visuel
- **🎲 Mélange automatique** : Randomisation des cartes et questions
- **📊 Suivi des scores** : Statistiques de performance

### Système de scores
- **Barème personnalisable** : Configuration des points 0-10
- **Impact sur le planning** : Ajustement automatique selon les résultats
- **Historique** : Suivi des performances par cours

---

## 🔧 **API Endpoints**

### Examens
- `GET /api/examens` - Lister tous les examens
- `POST /api/examens` - Créer un nouvel examen

### Cours
- `GET /api/cours?examen_id={id}` - Lister les cours d'un examen
- `POST /api/cours` - Ajouter un cours
- `PUT /api/cours/{id}` - Modifier un cours

### Planning
- `GET /api/planning/exam/{exam_id}` - Planning complet d'un examen
- `GET /api/planning/consolidated` - Planning consolidé avec détails
- `PUT /api/planning/{id}` - Marquer un élément comme effectué
- `GET /api/planning/conflicts` - Détecter les conflits
- `POST /api/planning/rebalance-global` - Rééquilibrer le planning

### Scores
- `GET /api/scores` - Lister tous les scores
- `POST /api/scores` - Enregistrer un score QCM

### Paramètres
- `GET /api/parametres` - Récupérer tous les paramètres
- `PUT /api/parametres/{key}` - Modifier un paramètre

### Barème
- `GET /api/bareme` - Récupérer le barème
- `PUT /api/bareme` - Modifier le barème complet

### Disponibilités
- `GET /api/disponibilite/weekly` - Récupérer les disponibilités hebdomadaires
- `PUT /api/disponibilite/weekly/{day}` - Modifier la disponibilité d'un jour

### Export/Import
- `GET /api/export` - Exporter toutes les données en JSON
- `POST /api/import` - Importer des données depuis un fichier JSON

---

## 📁 **Structure du fichier JSON**

```json
{
  "examens": [
    {
      "id": 1,
      "titre": "Examen S1",
      "date_exam": "2026-02-15",
      "type": "Partiel",
      "coefficient": 3
    }
  ],
  "cours": [
    {
      "id": 1,
      "titre": "Physio rein",
      "type": "Majeur",
      "priorite_indice": 8,
      "examen_id": 1,
      "duree_estimee": 60,
      "date_j0": "2025-09-20"
    }
  ],
  "planning": [
    {
      "id": 1,
      "cours_id": 1,
      "examen_id": 1,
      "jalon": 1,
      "date_finale": "2025-09-21",
      "duree": 45,
      "statut": "À faire",
      "type": "Majeur",
      "priorite_indice": 8
    }
  ],
  "scores": [
    {
      "id": 1,
      "cours_id": 1,
      "jalon": 1,
      "score": 8,
      "total": 10,
      "date_eval": "2025-09-23"
    }
  ],
  "parametres": [
    {"cle": "duree_min", "valeur": 30},
    {"cle": "duree_max", "valeur": 60},
    {"cle": "nb_max_par_j", "valeur": 4},
    {"cle": "bonus_ok", "valeur": 2},
    {"cle": "seuil_ok", "valeur": 85}
  ],
  "bareme": [
    {"indice": 0, "nb_revisions": 1},
    {"indice": 5, "nb_revisions": 6},
    {"indice": 10, "nb_revisions": 11}
  ],
  "disponibilites": [
    {"jour": "lundi", "minutes": 480},
    {"jour": "mardi", "minutes": 480}
  ]
}
```

---

## 🎯 **Algorithme de planning**

### Génération initiale
1. **Calcul des révisions** : Basé sur le barème (indice 0-10)
2. **Répartition temporelle** : Entre J0 et l'examen
3. **Respect des contraintes** : Durées min/max, plafond quotidien
4. **Priorisation** : Cours majeurs (priorité ≥ 7) conservent leur date

### Ajustement dynamique
- **Score < 60%** : Ajout d'une révision "JR..." avant l'examen
- **Score ≥ 85%** : Étirement de la révision suivante
- **Décalage automatique** : Cours non-prioritaires reportés si surcharge

---

## 🔐 **Authentification**

### Système de connexion
- **Identifiants fixes** : `camcam` / `202122`
- **Session** : 24 heures avec localStorage
- **Protection** : Toutes les pages sont protégées
- **Déconnexion** : Bouton disponible dans la navigation

### Sécurité
- Vérification automatique de session
- Redirection vers login si non connecté
- Prolongation automatique de session

---

## 📁 **Structure du projet**

```
revisioncam/
├── app_flask_json.py          # Application Flask principale
├── json_manager.py            # Gestionnaire de données JSON
├── migrate_to_json.py         # Script de migration SQLite → JSON
├── requirements.txt           # Dépendances Python
├── revisioncam.json          # Base de données JSON unique
├── revisioncam_backup.json   # Sauvegarde des données
├── README.md                 # Documentation
└── frontend/                 # Interface utilisateur
    ├── index.html            # Page d'accueil
    ├── cours.html            # Gestion des cours
    ├── planning.html         # Planning des révisions
    ├── scores.html           # Enregistrement des scores
    ├── parametres.html       # Configuration
    ├── login.html            # Page de connexion
    ├── qcm.html              # QCM interactifs
    ├── indexcardcamille.html # Cartes de révision
    ├── auth.js               # Système d'authentification
    ├── qcm.js                # Logique des QCM
    └── app.js                # Script général
```

---

## 🚀 **Déploiement**

### Serveur local
   ```bash
python app_flask_json.py
```

### Plateformes cloud
- **Render** : ✅ Compatible sans problème
- **Heroku** : ✅ Compatible
- **Railway** : ✅ Compatible
- **DigitalOcean** : ✅ Compatible

---

## 🔒 **Sécurité et sauvegarde**

### Sauvegarde automatique
- Chaque modification sauvegarde automatiquement le fichier JSON
- Pas de perte de données même en cas d'arrêt brutal
- Historique des modifications via le système de fichiers

### Intégrité des données
- Validation des structures JSON
- Contrôle des types de données
- Gestion des erreurs de corruption

---

## 🎉 **Avantages du système JSON**

Le **système JSON** transforme RevisionCam en une application **100% autonome** et **portable** :

- 🚀 **Plus simple** à déployer
- 📱 **Plus portable** entre appareils  
- 🔧 **Plus facile** à maintenir
- 💾 **Plus fiable** pour les sauvegardes
- ⚡ **Plus rapide** en performance

**RevisionCam est maintenant prêt pour n'importe quel hébergement !** 🎯

---

## 👥 **Auteur**

**Camille** - [@camcarre](https://github.com/camcarre)

---

*RevisionCam - Organisez vos révisions de manière intelligente* 🎓
## 🚀 Déploiement sur Render

### Configuration Render

Le projet est configuré pour être déployé sur Render avec les fichiers suivants :

- `requirements.txt` : Dépendances Python
- `render.yaml` : Configuration Render
- `start.sh` : Script de démarrage

### Variables d'environnement

Aucune variable d'environnement n'est requise. Le port est automatiquement configuré par Render.

### Déploiement

1. Connectez votre repository GitHub à Render
2. Sélectionnez le type "Web Service"
3. Render détectera automatiquement la configuration Python
4. Le déploiement se fera automatiquement

### URL de production

Une fois déployé, votre application sera disponible à l'URL fournie par Render.

### Identifiants par défaut

- **Utilisateur** : `camcam`
- **Mot de passe** : `202122`

