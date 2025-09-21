#!/bin/bash

# Script de build spécifique pour Render
echo "🚀 Build Render - RevisionCam"
echo "================================"

# Installer Python 3.11 si nécessaire
echo "🐍 Installation de Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    echo "Installation de Python 3.11..."
    # Utiliser pyenv ou installer depuis source
    curl -sSL https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz | tar -xz
    cd Python-3.11.9
    ./configure --prefix=/tmp/python311
    make -j$(nproc)
    make install
    export PATH="/tmp/python311/bin:$PATH"
    cd ..
fi

# Vérifier la version Python
echo "📋 Version Python:"
python3.11 --version || python --version

# Utiliser Python 3.11 si disponible
PYTHON_CMD="python"
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    export PYTHON_CMD
fi

# Mettre à jour pip
echo "📦 Mise à jour de pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Installer les dépendances minimales
echo "📦 Installation des dépendances..."
pip install -r requirements-minimal.txt

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
