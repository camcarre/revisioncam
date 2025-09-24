#!/usr/bin/env python3
"""
Script de migration SQLite vers JSON
Convertit toutes les données existantes vers le nouveau format JSON
"""

import sqlite3
import json
import os
from datetime import datetime
from json_manager import JSONDataManager

def migrate_sqlite_to_json(sqlite_file="revision.db", json_file="revisioncam.json"):
    """Migre toutes les données de SQLite vers JSON"""
    
    print(f"🔄 Migration de {sqlite_file} vers {json_file}...")
    
    # Initialiser le gestionnaire JSON
    json_manager = JSONDataManager(json_file)
    
    try:
        # Connexion à SQLite
        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # === MIGRATION DES EXAMENS ===
        print("📚 Migration des examens...")
        cursor.execute("SELECT * FROM examens")
        examens = cursor.fetchall()
        
        for exam in examens:
            exam_data = {
                "titre": exam['titre'],
                "date_exam": exam['date_exam']
            }
            json_manager.create_examen(exam_data)
        
        print(f"✅ {len(examens)} examens migrés")
        
        # === MIGRATION DES COURS ===
        print("📖 Migration des cours...")
        cursor.execute("SELECT * FROM cours")
        cours = cursor.fetchall()
        
        for cours_item in cours:
            cours_data = {
                "titre": cours_item['titre'],
                "type": cours_item['type'],
                "priorite_indice": cours_item['priorite_indice'],
                "examen_id": cours_item['examen_id'],
                "duree_estimee": cours_item['duree_estimee'],
                "date_j0": cours_item['date_j0']
            }
            json_manager.create_cours(cours_data)
        
        print(f"✅ {len(cours)} cours migrés")
        
        # === MIGRATION DU PLANNING ===
        print("📅 Migration du planning...")
        cursor.execute("SELECT * FROM planning")
        planning = cursor.fetchall()
        
        for plan_item in planning:
            planning_data = {
                "cours_id": plan_item['cours_id'],
                "examen_id": plan_item['examen_id'],
                "jalon": plan_item['jalon'],
                "date_finale": plan_item['date_finale'],
                "duree": plan_item['duree'],
                "statut": plan_item['statut']
            }
            
            # Récupérer les infos du cours pour type et priorite
            cursor.execute("SELECT type, priorite_indice FROM cours WHERE id = ?", (plan_item['cours_id'],))
            cours_info = cursor.fetchone()
            if cours_info:
                planning_data['type'] = cours_info['type']
                planning_data['priorite_indice'] = cours_info['priorite_indice']
            
            json_manager.create_planning_item(planning_data)
        
        print(f"✅ {len(planning)} éléments de planning migrés")
        
        # === MIGRATION DES SCORES ===
        print("📊 Migration des scores...")
        cursor.execute("SELECT * FROM scores")
        scores = cursor.fetchall()
        
        for score in scores:
            score_data = {
                "cours_id": score['cours_id'],
                "jalon": score['jalon'],
                "score": score['score'],
                "total": score['total'],
                "date_eval": score['date_eval']
            }
            json_manager.create_score(score_data)
        
        print(f"✅ {len(scores)} scores migrés")
        
        # === MIGRATION DES PARAMÈTRES ===
        print("⚙️ Migration des paramètres...")
        cursor.execute("SELECT * FROM parametres")
        parametres = cursor.fetchall()
        
        params_dict = {}
        for param in parametres:
            params_dict[param['cle']] = param['valeur']
        
        json_manager.update_parametres(params_dict)
        print(f"✅ {len(parametres)} paramètres migrés")
        
        # === MIGRATION DU BARÈME ===
        print("📋 Migration du barème...")
        cursor.execute("SELECT * FROM bareme")
        bareme = cursor.fetchall()
        
        bareme_list = []
        for item in bareme:
            bareme_list.append({
                "indice": item['indice'],
                "nb_revisions": item['nb_revisions']
            })
        
        json_manager.data['bareme'] = bareme_list
        json_manager._save_data()
        print(f"✅ {len(bareme)} éléments de barème migrés")
        
        # === MIGRATION DES DISPONIBILITÉS ===
        print("⏰ Migration des disponibilités...")
        cursor.execute("SELECT * FROM disponibilites")
        disponibilites = cursor.fetchall()
        
        dispo_list = []
        for dispo in disponibilites:
            dispo_list.append({
                "jour": dispo['jour'],
                "minutes": dispo['minutes']
            })
        
        json_manager.data['disponibilites'] = dispo_list
        json_manager._save_data()
        print(f"✅ {len(disponibilites)} disponibilités migrées")
        
        # Fermer la connexion SQLite
        conn.close()
        
        # Afficher les statistiques finales
        stats = json_manager.get_stats()
        print(f"\n🎉 MIGRATION TERMINÉE !")
        print(f"📊 Statistiques finales:")
        print(f"   • Examens: {stats['examens']}")
        print(f"   • Cours: {stats['cours']}")
        print(f"   • Planning: {stats['planning']}")
        print(f"   • Scores: {stats['scores']}")
        print(f"   • Paramètres: {stats['parametres']}")
        print(f"   • Barème: {stats['bareme']}")
        print(f"   • Disponibilités: {stats['disponibilites']}")
        
        print(f"\n💾 Fichier JSON créé: {json_file}")
        print(f"🗑️ Vous pouvez maintenant supprimer {sqlite_file}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def backup_sqlite(sqlite_file="revision.db"):
    """Crée une sauvegarde du fichier SQLite"""
    import shutil
    from datetime import datetime
    
    backup_name = f"{sqlite_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(sqlite_file, backup_name)
        print(f"💾 Sauvegarde créée: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    print("🔄 MIGRATION SQLITE → JSON")
    print("=" * 50)
    
    # Vérifier si le fichier SQLite existe
    sqlite_file = "revision.db"
    if not os.path.exists(sqlite_file):
        print(f"❌ Fichier {sqlite_file} non trouvé")
        print("💡 Assurez-vous que le fichier de base SQLite existe")
        sys.exit(1)
    
    # Créer une sauvegarde
    backup_file = backup_sqlite(sqlite_file)
    
    # Demander confirmation
    response = input(f"\n⚠️ Voulez-vous migrer {sqlite_file} vers JSON ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration annulée")
        sys.exit(0)
    
    # Effectuer la migration
    success = migrate_sqlite_to_json(sqlite_file)
    
    if success:
        print(f"\n✅ Migration réussie !")
        print(f"🚀 Vous pouvez maintenant utiliser app_flask_json.py")
        
        # Demander si on veut supprimer l'ancien fichier
        response = input(f"\n🗑️ Voulez-vous supprimer {sqlite_file} ? (y/N): ")
        if response.lower() == 'y':
            try:
                os.remove(sqlite_file)
                print(f"✅ {sqlite_file} supprimé")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression: {e}")
    else:
        print(f"\n❌ Migration échouée")
        print(f"💾 Sauvegarde disponible: {backup_file}")
        sys.exit(1)
