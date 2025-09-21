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

	// Ajouter le chemin des modules au PYTHONPATH
	cmd := exec.Command(pythonCmd, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", getPort())
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	// Ajouter le chemin des modules installés par pip
	cmd.Env = append(os.Environ(), 
		"PYTHONPATH=/opt/render/.local/lib/python3.11/site-packages:/opt/render/.local/lib/python3.11/dist-packages:"+os.Getenv("PYTHONPATH"))

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
