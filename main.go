package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	// Chercher Python 3.11 en priorité
	pythonCmd := "python3.11"
	if _, err := exec.LookPath(pythonCmd); err != nil {
		pythonCmd = "python3"
		if _, err := exec.LookPath(pythonCmd); err != nil {
			pythonCmd = "python"
			if _, err := exec.LookPath(pythonCmd); err != nil {
				log.Fatal("Python not found")
			}
		}
	}

	// Chemin vers l'application
	appPath := filepath.Join(".", "app", "main.py")
	
	// Vérifier si le fichier existe
	if _, err := os.Stat(appPath); os.IsNotExist(err) {
		log.Fatal("app/main.py not found")
	}

	// Debug: Vérifier où sont installés les modules
	fmt.Println("🔍 Debug: Recherche des modules Python...")
	debugCmd := exec.Command(pythonCmd, "-c", "import sys; print('Python paths:'); [print(p) for p in sys.path]")
	debugCmd.Stdout = os.Stdout
	debugCmd.Stderr = os.Stderr
	debugCmd.Run()
	
	// Debug: Lister les modules installés dans le bon répertoire
	fmt.Println("🔍 Debug: Modules installés dans /opt/render/.local/lib/python3.11/site-packages...")
	listCmd := exec.Command("ls", "-la", "/opt/render/.local/lib/python3.11/site-packages/")
	listCmd.Stdout = os.Stdout
	listCmd.Stderr = os.Stderr
	listCmd.Run()
	
	// Debug: Vérifier si le répertoire existe
	fmt.Println("🔍 Debug: Vérification de l'existence du répertoire...")
	checkCmd := exec.Command("ls", "-la", "/opt/render/.local/")
	checkCmd.Stdout = os.Stdout
	checkCmd.Stderr = os.Stderr
	checkCmd.Run()
	
	// Debug: Vérifier le répertoire bin mentionné dans le warning
	fmt.Println("🔍 Debug: Vérification de /opt/render/.local/bin...")
	binCmd := exec.Command("ls", "-la", "/opt/render/.local/bin/")
	binCmd.Stdout = os.Stdout
	binCmd.Stderr = os.Stderr
	binCmd.Run()
	
	// Debug: Chercher où sont installés les modules
	fmt.Println("🔍 Debug: Recherche des modules dans tous les répertoires possibles...")
	searchCmd := exec.Command("find", "/opt", "/usr", "/home", "-name", "uvicorn*", "-type", "d")
	searchCmd.Stdout = os.Stdout
	searchCmd.Stderr = os.Stderr
	searchCmd.Run()
	
	// Debug: Vérifier les variables d'environnement Python
	fmt.Println("🔍 Debug: Variables d'environnement Python...")
	envCmd := exec.Command(pythonCmd, "-c", "import os; print('PYTHONPATH:', os.environ.get('PYTHONPATH', 'Not set')); print('USER_BASE:', os.environ.get('USER_BASE', 'Not set'))")
	envCmd.Stdout = os.Stdout
	envCmd.Stderr = os.Stderr
	envCmd.Run()
	
	// Installation des dépendances au runtime
	fmt.Println("🔧 Installation des dépendances au runtime...")
	installCmd := exec.Command(pythonCmd, "-m", "pip", "install", "--break-system-packages", "--user", "fastapi==0.95.2", "uvicorn==0.22.0", "SQLAlchemy==1.4.53", "pydantic==1.10.12", "python-dateutil==2.8.2")
	installCmd.Stdout = os.Stdout
	installCmd.Stderr = os.Stderr
	installCmd.Run()
	
	// Debug: Vérifier où sont installés les modules après installation
	fmt.Println("🔍 Debug: Vérification du répertoire utilisateur après installation...")
	userBaseCmd := exec.Command(pythonCmd, "-c", "import site; print('USER_BASE:', site.getuserbase()); print('USER_SITE:', site.getusersitepackages())")
	userBaseCmd.Stdout = os.Stdout
	userBaseCmd.Stderr = os.Stderr
	userBaseCmd.Run()
	
	// Debug: Vérifier si uvicorn est maintenant installé
	fmt.Println("🔍 Debug: Test d'import uvicorn après installation...")
	importCmd := exec.Command(pythonCmd, "-c", "import uvicorn; print('uvicorn trouvé:', uvicorn.__file__)")
	importCmd.Stdout = os.Stdout
	importCmd.Stderr = os.Stderr
	importCmd.Run()

	// Ajouter le chemin des modules au PYTHONPATH
	cmd := exec.Command(pythonCmd, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", getPort())
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	// Ajouter le chemin des modules installés par pip (basé sur le warning)
	// Le warning indique que uvicorn est dans /opt/render/.local/bin
	cmd.Env = append(os.Environ(), 
		"PYTHONPATH=/opt/render/.local/lib/python3.11/site-packages:/usr/local/lib/python3.11/dist-packages:/usr/lib/python3/dist-packages:"+os.Getenv("PYTHONPATH"),
		"PATH=/opt/render/.local/bin:"+os.Getenv("PATH"))

	fmt.Println("🚀 Starting RevisionCam with Go wrapper...")
	fmt.Printf("📋 Using Python: %s\n", pythonCmd)
	fmt.Printf("🌐 Port: %s\n", getPort())

	// Lancer l'application
	if err := cmd.Run(); err != nil {
		log.Fatal("Failed to start application:", err)
	}
}

func getPort() string {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	return port
}
