#!/bin/bash

# Script de build spécifique pour Render
echo "🚀 Build Render - RevisionCam"
echo "================================"

# Installer Python 3.11
echo "🐍 Installation de Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    echo "Downloading Python 3.11.9..."
    wget -q https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
    tar -xzf Python-3.11.9.tgz
    cd Python-3.11.9
    ./configure --prefix=/tmp/python311 --enable-optimizations
    make -j$(nproc)
    make install
    export PATH="/tmp/python311/bin:$PATH"
    export PYTHON_CMD="/tmp/python311/bin/python3.11"
    cd ..
    echo "✅ Python 3.11.9 installé"
else
    export PYTHON_CMD="python3.11"
fi

# Vérifier la version Python
echo "📋 Version Python:"
$PYTHON_CMD --version

# Installer les dépendances avec wheels pré-compilés
echo "📦 Installation des dépendances (wheels pré-compilés)..."
$PYTHON_CMD -m pip install --only-binary=all fastapi==0.95.2 uvicorn==0.22.0 SQLAlchemy==1.4.53 pydantic==1.10.12 python-dateutil==2.8.2

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
