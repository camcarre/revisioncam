#!/bin/bash

# Script de build spécifique pour Render
echo "🚀 Build Render - RevisionCam"
echo "================================"

# Vérifier la version Python
echo "📋 Version Python:"
python --version

# Installer les dépendances minimales directement
echo "📦 Installation des dépendances..."
pip install fastapi==0.95.2 uvicorn==0.22.0 SQLAlchemy==1.4.53 pydantic==1.10.12 python-dateutil==2.8.2

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
