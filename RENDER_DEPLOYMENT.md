# 🚀 Guide de déploiement sur Render

## ⚠️ Configuration importante

Pour éviter les erreurs de compilation Rust, utilisez ces paramètres exacts :

### 📋 Paramètres du service Render

**Configuration de base :**
- **Name** : `revisioncam`
- **Environment** : `Python 3`
- **Plan** : `Free`

**Build Command :**
```bash
./build_render.sh
```

**Start Command :**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Variables d'environnement :**
- `PYTHON_VERSION` : `3.11.9` (obligatoire)
- `PORT` : `8000`

**⚠️ IMPORTANT :** Python 3.13 n'est pas compatible avec Pydantic 1.10.12

### 🔐 Identifiants de connexion

- **Utilisateur** : `camcam`
- **Mot de passe** : `202122`

### 🌐 URLs après déploiement

- **Page de connexion** : `https://votre-app.onrender.com/`
- **Interface principale** : `https://votre-app.onrender.com/static/index.html`
- **CardCamille** : `https://votre-app.onrender.com/static/cardcamille/index.html`

### 📁 Fichiers importants

- ✅ `requirements-minimal.txt` - Versions compatibles sans Rust
- ✅ `render.yaml` - Configuration automatique
- ✅ `Procfile` - Commande de démarrage
- ✅ `.python-version` - Version Python spécifiée
- ✅ `runtime.txt` - Version Python pour Render

### 🔧 Dépannage

**Si le build échoue :**
1. Vérifiez que vous utilisez `./build_render.sh`
2. Assurez-vous que `PYTHON_VERSION=3.11.9` (pas 3.13 !)
3. Vérifiez que le `Build Command` est correct

**Si l'application ne démarre pas :**
1. Vérifiez que le `Start Command` est correct
2. Assurez-vous que `PORT` est défini
3. Consultez les logs Render pour plus de détails

### ✅ Test local

Pour tester localement avec les mêmes versions :
```bash
pip install -r requirements-minimal.txt
python -m uvicorn app.main:app --reload
```

### 🎯 Fonctionnalités

- ✅ Interface Apple-style moderne
- ✅ Système d'authentification simple
- ✅ Planning de révisions adaptatif
- ✅ Module CardCamille intégré
- ✅ API FastAPI complète
- ✅ Base de données SQLite
- ✅ Interface responsive
