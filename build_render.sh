#!/bin/bash

# Script de build spécifique pour Render
echo "🚀 Build Render - RevisionCam"
echo "================================"

# Utiliser Python 3.11 disponible
echo "🐍 Utilisation de Python 3.11..."
export PYTHON_CMD="python3.11"

# Vérifier la version Python
echo "📋 Version Python:"
$PYTHON_CMD --version

# Installer les dépendances directement avec --break-system-packages
echo "📦 Installation des dépendances (wheels pré-compilés)..."
$PYTHON_CMD -m pip install --break-system-packages --only-binary=all fastapi==0.95.2 uvicorn==0.22.0 SQLAlchemy==1.4.53 pydantic==1.10.12 python-dateutil==2.8.2

# Vérifier les imports
echo "🔍 Test des imports..."
python -c "
try:
    from app.main import app
    print('✅ Import app.main réussi')
    
    from app.database import engine, SessionLocal
    print('✅ Import app.database réussi')
    
    from app.models import Base
    print('✅ Import app.models réussi')
    
    import app.schemas
    print('✅ Import app.schemas réussi')
    
    print('🎉 Tous les imports fonctionnent !')
except Exception as e:
    print(f'❌ Erreur d\'import: {e}')
    exit(1)
"

echo "✅ Build terminé avec succès !"
