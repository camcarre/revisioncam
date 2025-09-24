#!/usr/bin/env python3
"""
Gestionnaire de données JSON pour RevisionCam
Remplace complètement SQLite par un fichier JSON unique
"""

import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

class JSONDataManager:
    """Gestionnaire de données JSON avec verrouillage thread-safe"""
    
    def __init__(self, json_file: str = "revisioncam.json"):
        self.json_file = json_file
        self.data = self._load_default_data()
        self.lock = threading.Lock()
        self._load_data()
    
    def _load_default_data(self) -> Dict[str, Any]:
        """Structure par défaut du fichier JSON"""
        return {
            "examens": [],
            "cours": [],
            "planning": [],
            "scores": [],
            "parametres": {
                "duree_min": 30,
                "duree_max": 60,
                "nb_max_par_j": 4,
                "nb_min_par_j": 1,
                "bonus_ok": 2,
                "bonus_fail": 1,
                "seuil_ok": 85,
                "seuil_fail": 60,
                "temps_pause": 15
            },
            "bareme": [
                {"indice": 0, "nb_revisions": 1},
                {"indice": 1, "nb_revisions": 2},
                {"indice": 2, "nb_revisions": 3},
                {"indice": 3, "nb_revisions": 4},
                {"indice": 4, "nb_revisions": 5},
                {"indice": 5, "nb_revisions": 6},
                {"indice": 6, "nb_revisions": 7},
                {"indice": 7, "nb_revisions": 8},
                {"indice": 8, "nb_revisions": 9},
                {"indice": 9, "nb_revisions": 10},
                {"indice": 10, "nb_revisions": 11}
            ],
            "disponibilites": [
                {"jour": "lundi", "minutes": 480},
                {"jour": "mardi", "minutes": 480},
                {"jour": "mercredi", "minutes": 480},
                {"jour": "jeudi", "minutes": 480},
                {"jour": "vendredi", "minutes": 480},
                {"jour": "samedi", "minutes": 300},
                {"jour": "dimanche", "minutes": 240}
            ]
        }
    
    def _load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Fusionner avec les données par défaut pour les nouvelles clés
                    for key, default_value in self.data.items():
                        if key not in loaded_data:
                            loaded_data[key] = default_value
                    self.data = loaded_data
                print(f"✅ Données chargées depuis {self.json_file}")
            else:
                self._save_data()
                print(f"✅ Fichier {self.json_file} créé avec les données par défaut")
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            self.data = self._load_default_data()
            self._save_data()
    
    def _save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with self.lock:
                with open(self.json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                print(f"💾 Données sauvegardées dans {self.json_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def _get_next_id(self, table: str) -> int:
        """Génère le prochain ID pour une table"""
        if table not in self.data:
            return 1
        if not self.data[table]:
            return 1
        return max(item.get('id', 0) for item in self.data[table]) + 1
    
    # === MÉTHODES POUR LES EXAMENS ===
    def get_examens(self) -> List[Dict]:
        """Récupère tous les examens"""
        return self.data.get("examens", [])
    
    def get_examen(self, exam_id: int) -> Optional[Dict]:
        """Récupère un examen par ID"""
        for exam in self.data.get("examens", []):
            if exam.get("id") == exam_id:
                return exam
        return None
    
    def create_examen(self, exam_data: Dict) -> Dict:
        """Crée un nouvel examen"""
        exam_data["id"] = self._get_next_id("examens")
        self.data["examens"].append(exam_data)
        self._save_data()
        return exam_data
    
    def update_examen(self, exam_id: int, exam_data: Dict) -> bool:
        """Met à jour un examen"""
        for i, exam in enumerate(self.data["examens"]):
            if exam.get("id") == exam_id:
                exam_data["id"] = exam_id
                self.data["examens"][i] = exam_data
                self._save_data()
                return True
        return False
    
    def delete_examen(self, exam_id: int) -> bool:
        """Supprime un examen et ses données liées"""
        # Supprimer l'examen
        self.data["examens"] = [e for e in self.data["examens"] if e.get("id") != exam_id]
        
        # Supprimer les cours liés
        cours_to_delete = [c["id"] for c in self.data["cours"] if c.get("examen_id") == exam_id]
        self.data["cours"] = [c for c in self.data["cours"] if c.get("examen_id") != exam_id]
        
        # Supprimer le planning lié
        self.data["planning"] = [p for p in self.data["planning"] if p.get("examen_id") != exam_id]
        
        # Supprimer les scores liés
        for cours_id in cours_to_delete:
            self.data["scores"] = [s for s in self.data["scores"] if s.get("cours_id") != cours_id]
        
        self._save_data()
        return True
    
    # === MÉTHODES POUR LES COURS ===
    def get_cours(self, examen_id: Optional[int] = None) -> List[Dict]:
        """Récupère tous les cours ou ceux d'un examen spécifique"""
        cours = self.data.get("cours", [])
        if examen_id is not None:
            cours = [c for c in cours if c.get("examen_id") == examen_id]
        return cours
    
    def get_cours_by_id(self, cours_id: int) -> Optional[Dict]:
        """Récupère un cours par ID"""
        for cours in self.data.get("cours", []):
            if cours.get("id") == cours_id:
                return cours
        return None
    
    def create_cours(self, cours_data: Dict) -> Dict:
        """Crée un nouveau cours"""
        cours_data["id"] = self._get_next_id("cours")
        self.data["cours"].append(cours_data)
        self._save_data()
        return cours_data
    
    def update_cours(self, cours_id: int, cours_data: Dict) -> bool:
        """Met à jour un cours"""
        for i, cours in enumerate(self.data["cours"]):
            if cours.get("id") == cours_id:
                cours_data["id"] = cours_id
                self.data["cours"][i] = cours_data
                self._save_data()
                return True
        return False
    
    def delete_cours(self, cours_id: int) -> bool:
        """Supprime un cours et ses données liées"""
        # Supprimer le cours
        self.data["cours"] = [c for c in self.data["cours"] if c.get("id") != cours_id]
        
        # Supprimer le planning lié
        self.data["planning"] = [p for p in self.data["planning"] if p.get("cours_id") != cours_id]
        
        # Supprimer les scores liés
        self.data["scores"] = [s for s in self.data["scores"] if s.get("cours_id") != cours_id]
        
        self._save_data()
        return True
    
    # === MÉTHODES POUR LE PLANNING ===
    def get_planning(self, examen_id: Optional[int] = None) -> List[Dict]:
        """Récupère le planning, optionnellement filtré par examen"""
        planning = self.data.get("planning", [])
        if examen_id is not None:
            planning = [p for p in planning if p.get("examen_id") == examen_id]
        return planning
    
    def create_planning_item(self, planning_data: Dict) -> Dict:
        """Crée un nouvel élément de planning"""
        planning_data["id"] = self._get_next_id("planning")
        self.data["planning"].append(planning_data)
        self._save_data()
        return planning_data
    
    def update_planning_item(self, planning_id: int, planning_data: Dict) -> bool:
        """Met à jour un élément de planning"""
        for i, item in enumerate(self.data["planning"]):
            if item.get("id") == planning_id:
                planning_data["id"] = planning_id
                self.data["planning"][i] = planning_data
                self._save_data()
                return True
        return False
    
    def delete_planning_item(self, planning_id: int) -> bool:
        """Supprime un élément de planning"""
        self.data["planning"] = [p for p in self.data["planning"] if p.get("id") != planning_id]
        self._save_data()
        return True
    
    def clear_planning_for_exam(self, examen_id: int, keep_status: str = None):
        """Supprime le planning d'un examen, optionnellement en gardant certains statuts"""
        if keep_status:
            self.data["planning"] = [
                p for p in self.data["planning"] 
                if p.get("examen_id") != examen_id or p.get("statut") == keep_status
            ]
        else:
            self.data["planning"] = [p for p in self.data["planning"] if p.get("examen_id") != examen_id]
        self._save_data()
    
    # === MÉTHODES POUR LES SCORES ===
    def get_scores(self, cours_id: Optional[int] = None) -> List[Dict]:
        """Récupère tous les scores ou ceux d'un cours spécifique"""
        scores = self.data.get("scores", [])
        if cours_id is not None:
            scores = [s for s in scores if s.get("cours_id") == cours_id]
        return scores
    
    def create_score(self, score_data: Dict) -> Dict:
        """Crée un nouveau score"""
        score_data["id"] = self._get_next_id("scores")
        self.data["scores"].append(score_data)
        self._save_data()
        return score_data
    
    # === MÉTHODES POUR LES PARAMÈTRES ===
    def get_parametres(self) -> Dict:
        """Récupère tous les paramètres"""
        return self.data.get("parametres", {})
    
    def get_parametre(self, key: str) -> Any:
        """Récupère un paramètre spécifique"""
        return self.data.get("parametres", {}).get(key)
    
    def update_parametre(self, key: str, value: Any) -> bool:
        """Met à jour un paramètre"""
        if "parametres" not in self.data:
            self.data["parametres"] = {}
        self.data["parametres"][key] = value
        self._save_data()
        return True
    
    def update_parametres(self, params: Dict) -> bool:
        """Met à jour plusieurs paramètres"""
        if "parametres" not in self.data:
            self.data["parametres"] = {}
        self.data["parametres"].update(params)
        self._save_data()
        return True
    
    # === MÉTHODES POUR LE BARÈME ===
    def get_bareme(self) -> List[Dict]:
        """Récupère le barème"""
        return self.data.get("bareme", [])
    
    def get_nb_revisions(self, indice: int) -> int:
        """Récupère le nombre de révisions pour un indice donné"""
        indice = max(0, min(10, int(indice) if indice is not None else 5))
        for item in self.data.get("bareme", []):
            if item.get("indice") == indice:
                return item.get("nb_revisions", 3)
        return 3  # Valeur par défaut
    
    # === MÉTHODES POUR LES DISPONIBILITÉS ===
    def get_disponibilites(self) -> List[Dict]:
        """Récupère les disponibilités"""
        return self.data.get("disponibilites", [])
    
    def update_disponibilites(self, disponibilites: List[Dict]) -> bool:
        """Met à jour les disponibilités"""
        self.data["disponibilites"] = disponibilites
        self._save_data()
        return True
    
    # === MÉTHODES D'IMPORT/EXPORT ===
    def export_data(self) -> Dict:
        """Exporte toutes les données"""
        return self.data.copy()
    
    def import_data(self, data: Dict) -> bool:
        """Importe des données et remplace tout"""
        try:
            # Valider la structure
            required_keys = ["examens", "cours", "planning", "scores", "parametres", "bareme", "disponibilites"]
            for key in required_keys:
                if key not in data:
                    data[key] = self._load_default_data()[key]
            
            self.data = data
            self._save_data()
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques du système"""
        return {
            "examens": len(self.data.get("examens", [])),
            "cours": len(self.data.get("cours", [])),
            "planning": len(self.data.get("planning", [])),
            "scores": len(self.data.get("scores", [])),
            "parametres": len(self.data.get("parametres", {})),
            "bareme": len(self.data.get("bareme", [])),
            "disponibilites": len(self.data.get("disponibilites", []))
        }

# Instance globale du gestionnaire
json_manager = JSONDataManager()

