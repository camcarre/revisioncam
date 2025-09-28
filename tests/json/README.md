# 📋 Fichiers JSON de Test - RevisionCam

Ce dossier contient différents fichiers JSON de test pour tester les différentes fonctionnalités de l'application RevisionCam.

## 📁 Fichiers Disponibles

### 🎯 **test-complet.json**
**Données complètes pour tous les tests**
- ✅ 4 examens (Anatomie, Physiologie, Pharmacologie, Pathologie)
- ✅ 8 cours avec différentes priorités (indices 4-9)
- ✅ 25 éléments de planning générés automatiquement
- ✅ 3 scores existants pour tester l'algorithme d'ajustement
- ✅ Tous les paramètres et configurations

**Usage :** Test complet de toutes les fonctionnalités

---

### 📅 **test-planning-seul.json**
**Focus sur le planning et les statuts**
- ✅ 2 examens de test
- ✅ 3 cours avec différentes priorités
- ✅ 24 éléments de planning avec statuts variés :
  - **"Fait"** : Révisions terminées
  - **"À faire"** : Révisions en attente
  - **"Reporté"** : Révisions décalées
- ❌ Aucun score (pour tester la synchronisation planning → scores)

**Usage :** Test de la gestion des statuts et de la synchronisation

---

### 📚 **test-cours-seul.json**
**Focus sur la gestion des cours**
- ✅ 5 examens (Anatomie, Physiologie, Pharmacologie, Pathologie, Chirurgie)
- ✅ 25 cours détaillés avec :
  - Différentes priorités (indices 4-9)
  - Types variés (Majeur/Mineur)
  - Durées réalistes (45-120 min)
  - Dates de début (date_j0)
- ❌ Aucun planning généré
- ❌ Aucun score

**Usage :** Test de la génération de planning et des jalons dynamiques

---

### 📊 **test-scores-seul.json**
**Focus sur les scores et l'algorithme d'ajustement**
- ✅ 3 examens de test
- ✅ 5 cours avec planning généré
- ✅ 10 scores avec différents niveaux :
  - **Scores élevés** (88-95%) → Test espacement
  - **Scores moyens** (65-78%) → Pas d'ajustement
  - **Scores faibles** (38-45%) → Test révisions supplémentaires
- ✅ Planning correspondant marqué "Fait"

**Usage :** Test de l'algorithme d'ajustement basé sur les scores

---

### 🎓 **test-examens-seul.json**
**Focus sur la gestion des examens**
- ✅ 10 examens variés :
  - Types différents (Partiel, Contrôle, QCM, Oral, Final)
  - Dates échelonnées sur 10 mois
  - Domaines médicaux variés
- ❌ Aucun cours associé
- ❌ Aucun planning
- ❌ Aucun score

**Usage :** Test de l'ajout de cours et de la génération de planning

---

### 🔄 **test-vide.json**
**Reset complet de l'application**
- ❌ Aucune donnée utilisateur
- ✅ Paramètres par défaut conservés
- ✅ Barème standard
- ✅ Disponibilités hebdomadaires

**Usage :** Remise à zéro pour repartir sur des bases propres

---

## 🚀 Comment Utiliser

### **1. Import via l'Interface Web**
1. Va sur la page **Cours** ou **Scores**
2. Clique sur **"Importer des données"**
3. Sélectionne le fichier JSON de test souhaité
4. Confirme l'import

### **2. Import Direct (Backend)**
```bash
# Copier un fichier de test
cp tests/json/test-complet.json revisioncam.json

# Redémarrer l'application
python app_flask_json.py
```

---

## 🧪 Scénarios de Test Recommandés

### **Test 1 : Jalons Dynamiques**
1. Import `test-cours-seul.json`
2. Va sur **Scores**
3. Sélectionne un cours → Vérifie que les jalons se chargent
4. Test avec différents cours (priorités différentes)

### **Test 2 : Synchronisation Planning ↔ Scores**
1. Import `test-planning-seul.json`
2. Va sur **Planning** → Marque des révisions "Fait"
3. Va sur **Scores** → Vérifie que les scores par défaut sont créés
4. Va sur **Scores** → Ajoute un score
5. Retour sur **Planning** → Vérifie que c'est marqué "Fait"

### **Test 3 : Algorithme d'Ajustement**
1. Import `test-scores-seul.json`
2. Va sur **Scores** → Ajoute un score faible (< 60%)
3. Va sur **Planning** → Vérifie qu'une révision supplémentaire est ajoutée
4. Ajoute un score élevé (≥ 85%)
5. Vérifie que les révisions suivantes sont espacées

### **Test 4 : Conflits et Rééquilibrage**
1. Import `test-complet.json`
2. Va sur **Planning** → Sélectionne un examen
3. Clique sur **"Détecter les conflits"**
4. Clique sur **"Rééquilibrer automatiquement"**
5. Vérifie les ajustements proposés

### **Test 5 : Gestion des Examens**
1. Import `test-examens-seul.json`
2. Va sur **Paramètres** → Section "Gestion des examens"
3. Ajoute quelques cours aux examens
4. Génère le planning
5. Teste les jalons dynamiques

---

## 📝 Notes Importantes

- **Sauvegarde** : Toujours exporter tes données avant d'importer un fichier de test
- **Reset** : Utilise `test-vide.json` pour une remise à zéro complète
- **Compatibilité** : Tous les fichiers sont compatibles avec la version actuelle
- **Logs** : Les actions sont loggées dans la console du navigateur (F12)

---

## 🎯 Objectifs des Tests

- ✅ **Jalons dynamiques** : Vérifier le calcul basé sur `priorite_indice`
- ✅ **Synchronisation** : Planning et scores restent cohérents
- ✅ **Algorithme** : Ajustements basés sur les scores fonctionnent
- ✅ **Interface** : Toutes les pages se chargent correctement
- ✅ **Performance** : L'application reste réactive avec des données
- ✅ **Robustesse** : Gestion des cas limites et erreurs
