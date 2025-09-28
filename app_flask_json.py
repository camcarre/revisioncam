#!/usr/bin/env python3
"""
Application RevisionCam avec Flask et JSON
Remplace complètement SQLite par un fichier JSON unique
"""

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

# Import du gestionnaire JSON
from json_manager import json_manager

app = Flask(__name__)
CORS(app, origins=['https://revisioncam-1.onrender.com', 'http://localhost:8080', 'http://127.0.0.1:8080'])  # Enable CORS for all routes

# Configuration
FRONTEND_DIR = Path(__file__).parent / "frontend"

# Algorithm constants
OFFSETS_TEMPLATE = [1, 3, 7, 14, 21, 30, 45, 60, 75, 90, 105, 120, 135]
DURATION_FACTORS = [0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.15, 0.12, 0.12, 0.1, 0.1]

@dataclass
class PlanningParams:
    duree_min: int
    duree_max: int
    nb_max_par_j: int
    default_daily_minutes: int
    revision_finale_jours: int = 7
    min_gap_days: int = 2
    bonus_ok_days: int = 2

@dataclass
class DayState:
    total_duration: int
    count: int

def load_params() -> PlanningParams:
    """Charge les paramètres depuis le JSON"""
    params = json_manager.get_parametres()
    return PlanningParams(
        duree_min=params.get('duree_min', 30),
        duree_max=params.get('duree_max', 60),
        nb_max_par_j=params.get('nb_max_par_j', 4),
        default_daily_minutes=480,
        revision_finale_jours=7,
        min_gap_days=2,
        bonus_ok_days=params.get('bonus_ok', 2)
    )

def get_availability_map() -> Dict[str, int]:
    """Récupère la carte des disponibilités depuis le JSON"""
    disponibilites = json_manager.get_disponibilites()
    availability_map = {}
    for dispo in disponibilites:
        availability_map[dispo['jour']] = dispo['minutes']
    return availability_map

def get_nb_revisions(indice: int) -> int:
    """Récupère le nombre de révisions pour un indice donné"""
    return json_manager.get_nb_revisions(indice)

def init_data():
    """Initialise les données avec des exemples si nécessaire"""
    stats = json_manager.get_stats()
    
    # Si pas d'examens, créer des données de test
    if stats['examens'] == 0:
        print("📝 Création des données de test...")
        
        # Créer des examens de test
        examens_test = [
            {"titre": "Examen S1", "date_exam": "2026-02-15"},
            {"titre": "Examen S2", "date_exam": "2026-06-10"},
            {"titre": "Rattrapages S1", "date_exam": "2026-03-15"},
            {"titre": "Rattrapages S2", "date_exam": "2026-07-05"},
            {"titre": "Partiels S1", "date_exam": "2026-01-20"},
            {"titre": "Partiels S2", "date_exam": "2026-05-15"},
            {"titre": "Examens finaux", "date_exam": "2026-08-20"},
            {"titre": "Examens spéciaux", "date_exam": "2026-09-10"}
        ]
        
        for exam_data in examens_test:
            json_manager.create_examen(exam_data)
        
        # Créer des cours de test pour le premier examen
        exam_id = 1
        cours_test = [
            {"titre": "Physio rein modifié", "type": "Majeur", "priorite_indice": 8, "examen_id": exam_id, "duree_estimee": 60, "date_j0": "2025-09-20"},
            {"titre": "Anatomie coeur", "type": "Majeur", "priorite_indice": 7, "examen_id": exam_id, "duree_estimee": 90, "date_j0": "2025-09-20"},
            {"titre": "Biochimie glucose", "type": "Majeur", "priorite_indice": 9, "examen_id": exam_id, "duree_estimee": 75, "date_j0": "2025-09-20"},
            {"titre": "Pharmacologie", "type": "Mineur", "priorite_indice": 5, "examen_id": exam_id, "duree_estimee": 45, "date_j0": "2025-09-20"},
            {"titre": "Pathologie", "type": "Majeur", "priorite_indice": 6, "examen_id": exam_id, "duree_estimee": 80, "date_j0": "2025-09-20"}
        ]
        
        for cours_data in cours_test:
            json_manager.create_cours(cours_data)
        
        # Générer le planning pour le premier examen
        regenerate_planning_for_exam(exam_id)
        
        print(f"✅ {stats['examens']} examens et {len(cours_test)} cours créés avec planning")

# === ALGORITHME DE PLANNING ===

def generate_planning_for_course(course: Dict, exam: Dict, params: PlanningParams, availability_map: Dict[str, int]) -> List[Dict]:
    """Génère le planning pour un cours spécifique"""
    exam_date = datetime.strptime(exam['date_exam'], '%Y-%m-%d').date()
    
    # Si date_j0 n'est pas fournie, utiliser la date de création du cours ou une date par défaut
    if 'date_j0' in course and course['date_j0']:
        course_start = datetime.strptime(course['date_j0'], '%Y-%m-%d').date()
    else:
        # Utiliser la date actuelle comme date de début
        course_start = datetime.now().date()
    
    nb_revisions = get_nb_revisions(course.get('priorite_indice', 5))
    planning_items = []
    
    # Calculer les dates des jalons
    for i in range(nb_revisions):
        if i == 0:
            # Premier jalon : J+1 après le cours
            jalon_date = course_start + timedelta(days=1)
        elif i == nb_revisions - 1:
            # Dernier jalon : révision finale obligatoire
            jalon_date = exam_date - timedelta(days=params.revision_finale_jours)
        else:
            # Jalons intermédiaires basés sur la courbe d'oubli
            offset_days = OFFSETS_TEMPLATE[min(i, len(OFFSETS_TEMPLATE) - 1)]
            jalon_date = course_start + timedelta(days=offset_days)
        
        # Ajuster la durée selon le jalon
        duration_factor = DURATION_FACTORS[min(i, len(DURATION_FACTORS) - 1)]
        duration = max(params.duree_min, min(params.duree_max, int(float(course.get('duree_estimee', 30)) * duration_factor)))
        
        planning_item = {
            'cours_id': course['id'],
            'examen_id': exam['id'],
            'jalon': i + 1,
            'date_finale': jalon_date.strftime('%Y-%m-%d'),
            'duree': duration,
            'statut': 'À faire',
            'type': course['type'],
            'priorite_indice': course['priorite_indice']
        }
        
        planning_items.append(planning_item)
    
    return planning_items

def regenerate_planning_for_exam(exam_id: int):
    """Régénère le planning pour un examen (préserve les statuts 'Fait')"""
    exam = json_manager.get_examen(exam_id)
    if not exam:
        return
    
    # Supprimer seulement les éléments 'À faire'
    json_manager.clear_planning_for_exam(exam_id, keep_status='Fait')
    
    # Récupérer les cours de l'examen
    cours = json_manager.get_cours(exam_id)
    if not cours:
        return
    
    params = load_params()
    availability_map = get_availability_map()
    
    # Générer le planning pour chaque cours
    for course in cours:
        planning_items = generate_planning_for_course(course, exam, params, availability_map)
        for item in planning_items:
            json_manager.create_planning_item(item)

def detect_conflicts(params: PlanningParams) -> List[Dict]:
    """Détecte les conflits de planning"""
    # Récupérer max_revisions_per_day depuis les paramètres
    parametres = json_manager.get_parametres()
    max_revisions_per_day = parametres.get('max_revisions_per_day', 3)
    
    # Récupérer les disponibilités hebdomadaires
    availability_map = get_availability_map()
    
    print(f"🔍 Détection des conflits avec les seuils: nb_max={params.nb_max_par_j}, duree_max={params.default_daily_minutes}, max_revisions_per_day={max_revisions_per_day}")
    
    planning = json_manager.get_planning()
    print(f"📋 Éléments de planning à analyser: {len(planning)}")
    
    conflicts = []
    
    # Grouper par date
    daily_stats = {}
    for item in planning:
        if item.get('statut') != 'Fait':
            date_key = item['date_finale']
            if date_key not in daily_stats:
                daily_stats[date_key] = {'count': 0, 'duration': 0}
            daily_stats[date_key]['count'] += 1
            daily_stats[date_key]['duration'] += item.get('duree', 0)
    
    print(f"📊 Statistiques quotidiennes calculées pour {len(daily_stats)} dates")
    
    # Mapping des jours de la semaine
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    
    # Identifier les conflits
    for date_key, stats in daily_stats.items():
        # Calculer la disponibilité pour ce jour de la semaine
        date_obj = datetime.strptime(date_key, '%Y-%m-%d').date()
        day_of_week = days_of_week[date_obj.weekday()]
        day_availability = availability_map.get(day_of_week, params.default_daily_minutes)
        
        # Utiliser max_revisions_per_day et la disponibilité du jour
        max_daily_minutes = min(day_availability, params.default_daily_minutes)
        
        if stats['count'] > max_revisions_per_day or stats['duration'] > max_daily_minutes:
            print(f"⚠️ Conflit détecté le {date_key} ({day_of_week}): {stats['count']} révisions ({stats['duration']} min) - Disponibilité: {day_availability} min")
            conflicts.append({
                'date_finale': date_key,
                'nb_revisions': stats['count'],
                'total_duree': stats['duration']
            })
    
    print(f"📈 Total des conflits détectés: {len(conflicts)}")
    return conflicts

def rebalance_planning(exam_id: int, params: PlanningParams) -> Dict:
    """Rééquilibre le planning d'un examen"""
    print(f"🔍 Détection des conflits pour l'examen {exam_id}")
    conflicts = detect_conflicts(params)
    print(f"📊 Conflits détectés: {len(conflicts)}")
    adjustments = 0
    
    # Récupérer les cours pour avoir les priorités
    cours_list = json_manager.get_cours()
    cours_dict = {c['id']: c for c in cours_list}
    print(f"📚 Cours disponibles: {len(cours_dict)}")
    
    for conflict in conflicts:
        print(f"🔧 Traitement du conflit du {conflict['date_finale']} avec {conflict['nb_revisions']} révisions")
        
        # Récupérer les éléments de planning pour cette date et cet examen
        planning_items = [p for p in json_manager.get_planning() 
                         if p.get('date_finale') == conflict['date_finale'] and p.get('examen_id') == exam_id and p.get('statut') != 'Fait']
        print(f"📋 Éléments de planning trouvés: {len(planning_items)}")
        
        # Enrichir avec les informations des cours pour le tri
        enriched_items = []
        for item in planning_items:
            cours = cours_dict.get(item.get('cours_id', 0), {})
            enriched_item = {
                **item,
                'type': cours.get('type', 'Mineur'),
                'priorite_indice': cours.get('priorite_indice', 0)
            }
            enriched_items.append(enriched_item)
        
        # Trier par priorité (majeurs d'abord, puis par indice)
        enriched_items.sort(key=lambda x: (x['type'] != 'Majeur', int(x.get('priorite_indice', 0))), reverse=True)
        print(f"📊 Éléments triés par priorité: {[(item['type'], item['priorite_indice']) for item in enriched_items]}")
        
        # Garder les plus prioritaires
        keep_items = enriched_items[:params.nb_max_par_j]
        move_items = enriched_items[params.nb_max_par_j:]
        print(f"✅ Éléments à garder: {len(keep_items)}, 🔄 Éléments à déplacer: {len(move_items)}")
        
        # Déplacer les éléments moins prioritaires
        for item in move_items:
            print(f"🔍 Recherche d'un nouveau slot pour l'élément {item['id']}")
            new_date = find_slot(item, params)
            if new_date:
                print(f"✅ Nouveau slot trouvé: {new_date} (ancien: {item['date_finale']})")
                item['date_finale'] = new_date
                json_manager.update_planning_item(item['id'], item)
                adjustments += 1
            else:
                print(f"❌ Aucun slot disponible pour l'élément {item['id']}")
    
    print(f"📊 Résultat final: {adjustments} ajustements effectués, {len(conflicts)} conflits résolus")
    return {
        'adjustments': adjustments, 
        'conflicts_resolved': len(conflicts),
        'adjustment_details': []  # Pour compatibilité, on pourrait aussi ajouter les détails ici
    }

def rebalance_planning_global(params: PlanningParams) -> Dict:
    """Rééquilibre le planning global en traitant tous les conflits"""
    print(f"🌍 Début du rééquilibrage GLOBAL")
    conflicts = detect_conflicts(params)
    print(f"📊 Conflits globaux détectés: {len(conflicts)}")
    adjustments = 0
    adjustment_details = []  # Pour stocker les détails des ajustements
    
    # Récupérer les cours pour avoir les priorités
    cours_list = json_manager.get_cours()
    cours_dict = {c['id']: c for c in cours_list}
    print(f"📚 Cours disponibles: {len(cours_dict)}")
    
    for conflict in conflicts:
        print(f"🔧 Traitement du conflit GLOBAL du {conflict['date_finale']} avec {conflict['nb_revisions']} révisions")
        
        # Récupérer TOUS les éléments de planning pour cette date (tous examens)
        planning_items = [p for p in json_manager.get_planning() 
                         if p.get('date_finale') == conflict['date_finale'] and p.get('statut') != 'Fait']
        print(f"📋 Éléments de planning trouvés (tous examens): {len(planning_items)}")
        
        # Enrichir avec les informations des cours pour le tri
        enriched_items = []
        for item in planning_items:
            cours = cours_dict.get(item.get('cours_id', 0), {})
            enriched_item = {
                **item,
                'type': cours.get('type', 'Mineur'),
                'priorite_indice': cours.get('priorite_indice', 0),
                'examen_titre': json_manager.get_examen(item.get('examen_id', 0)).get('titre', 'Inconnu') if json_manager.get_examen(item.get('examen_id', 0)) else 'Inconnu'
            }
            enriched_items.append(enriched_item)
        
        # Trier par priorité (majeurs d'abord, puis par indice)
        enriched_items.sort(key=lambda x: (x['type'] != 'Majeur', int(x.get('priorite_indice', 0))), reverse=True)
        print(f"📊 Éléments triés par priorité: {[(item['type'], item['priorite_indice'], item['examen_titre']) for item in enriched_items]}")
        
        # Garder les plus prioritaires
        keep_items = enriched_items[:params.nb_max_par_j]
        move_items = enriched_items[params.nb_max_par_j:]
        print(f"✅ Éléments à garder: {len(keep_items)}, 🔄 Éléments à déplacer: {len(move_items)}")
        
        # Déplacer les éléments moins prioritaires
        for item in move_items:
            print(f"🔍 Recherche d'un nouveau slot pour l'élément {item['id']} (examen {item['examen_titre']})")
            old_date = item['date_finale']
            new_date = find_slot(item, params)
            if new_date:
                print(f"✅ Nouveau slot trouvé: {new_date} (ancien: {old_date})")
                item['date_finale'] = new_date
                json_manager.update_planning_item(item['id'], item)
                adjustments += 1
                
                # Ajouter les détails de l'ajustement
                adjustment_details.append({
                    'cours_id': item.get('cours_id'),
                    'cours_nom': cours_dict.get(item.get('cours_id', 0), {}).get('titre', 'Cours inconnu'),
                    'jalon': item.get('jalon'),
                    'ancienne_date': old_date,
                    'nouvelle_date': new_date,
                    'duree': item.get('duree')
                })
            else:
                print(f"❌ Aucun slot disponible pour l'élément {item['id']}")
    
    print(f"📊 Résultat final: {adjustments} ajustements effectués, {len(conflicts)} conflits résolus")
    return {
        'adjustments': adjustments, 
        'conflicts_resolved': len(conflicts),
        'adjustment_details': adjustment_details
    }

def find_slot(item: Dict, params: PlanningParams) -> Optional[str]:
    """Trouve un créneau disponible pour un élément de planning"""
    exam = json_manager.get_examen(item.get('examen_id', 0))
    if not exam:
        return None
    
    exam_date = datetime.strptime(exam['date_exam'], '%Y-%m-%d').date()
    candidate = datetime.strptime(item.get('date_finale', '2025-01-01'), '%Y-%m-%d').date()
    
    # Récupérer les disponibilités hebdomadaires
    availability_map = get_availability_map()
    
    # Mapping des jours de la semaine
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    
    while candidate < exam_date:
        # Vérifier si le jour de la semaine est disponible
        day_of_week = days_of_week[candidate.weekday()]
        day_availability = availability_map.get(day_of_week, 0)
        
        if day_availability <= 0:
            # Jour non disponible, passer au suivant
            candidate += timedelta(days=1)
            continue
        
        # Vérifier la disponibilité pour cette date
        daily_planning = [p for p in json_manager.get_planning()
                         if p.get('date_finale') == candidate.strftime('%Y-%m-%d') and p.get('statut') != 'Fait']
        
        total_duration = sum(p.get('duree', 0) for p in daily_planning)
        count = len(daily_planning)
        
        # Vérifier le respect du délai minimum entre révisions du même cours
        cours_id = item.get('cours_id')
        min_gap_ok = True
        if cours_id and params.min_gap_days > 0:
            # Chercher la dernière révision de ce cours
            cours_planning = [p for p in json_manager.get_planning()
                             if p.get('cours_id') == cours_id and p.get('statut') != 'Fait' and p.get('id') != item.get('id')]
            if cours_planning:
                # Trier par date pour trouver la plus récente
                cours_planning.sort(key=lambda x: datetime.strptime(x.get('date_finale', '2025-01-01'), '%Y-%m-%d'))
                last_revision_date = datetime.strptime(cours_planning[-1].get('date_finale', '2025-01-01'), '%Y-%m-%d').date()
                days_gap = (candidate - last_revision_date).days
                if days_gap < params.min_gap_days:
                    min_gap_ok = False
        
        # Récupérer max_revisions_per_day depuis les paramètres
        parametres = json_manager.get_parametres()
        max_revisions_per_day = parametres.get('max_revisions_per_day', 3)
        
        # Utiliser la disponibilité du jour ou la limite par défaut
        max_daily_minutes = min(day_availability, params.default_daily_minutes)
        
        if count < max_revisions_per_day and total_duration + item.get('duree', 0) <= max_daily_minutes and min_gap_ok:
            return candidate.strftime('%Y-%m-%d')
        
        candidate += timedelta(days=1)
    
    return None

def adjust_planning_with_score(course_id: int, jalon: int, score: int, total: int, date_eval: str = None):
    """Ajuste le planning selon un score QCM"""
    ratio = score / total
    params = load_params()
    
    print(f"📊 Ajustement planning pour cours {course_id}, jalon {jalon}, score {score}/{total} (ratio: {ratio:.2f})")
    if date_eval:
        print(f"📅 Date d'évaluation: {date_eval}")
    
    if ratio < 0.6:  # Score faible
        add_extra_revision_after_score(course_id, jalon, score, total, date_eval)
    elif ratio >= 0.85:  # Score excellent
        adjust_planning_after_high_score(course_id, jalon, params, date_eval)

def add_extra_revision_after_score(course_id: int, jalon: int, score: int, total: int, date_eval: str = None):
    """Ajoute une révision supplémentaire après un score faible"""
    course = json_manager.get_cours_by_id(course_id)
    if not course:
        return
    
    exam = json_manager.get_examen(course['examen_id'])
    if not exam:
        return
    
    # Utiliser la date d'évaluation si fournie, sinon utiliser la date actuelle
    if date_eval:
        eval_date = datetime.strptime(date_eval, '%Y-%m-%d').date()
        jalon_date = eval_date + timedelta(days=2)  # 2 jours après l'évaluation
    else:
        # Date de la révision supplémentaire : 2 jours après aujourd'hui
        jalon_date = datetime.now().date() + timedelta(days=2)
    
    print(f"📅 Révision supplémentaire prévue le {jalon_date.strftime('%Y-%m-%d')}")
    
    extra_revision = {
        'cours_id': course_id,
        'examen_id': course['examen_id'],
        'jalon': jalon + 1,
        'date_finale': jalon_date.strftime('%Y-%m-%d'),
        'duree': 30,  # Durée courte pour révision supplémentaire
        'statut': 'À faire',
        'type': course['type'],
        'priorite_indice': course['priorite_indice']
    }
    
    json_manager.create_planning_item(extra_revision)

def adjust_planning_after_high_score(course_id: int, jalon: int, params: PlanningParams, date_eval: str = None):
    """Espace les révisions suivantes après un bon score"""
    planning_items = [p for p in json_manager.get_planning() 
                     if p.get('cours_id') == course_id and p.get('jalon', 0) > jalon and p.get('statut') == 'À faire']
    
    print(f"📊 Espacement de {len(planning_items)} révisions après bon score")
    if date_eval:
        print(f"📅 Date d'évaluation: {date_eval}")
    
    for item in planning_items:
        current_date = datetime.strptime(item['date_finale'], '%Y-%m-%d').date()
        new_date = current_date + timedelta(days=params.bonus_ok_days)
        item['date_finale'] = new_date.strftime('%Y-%m-%d')
        json_manager.update_planning_item(item['id'], item)
        print(f"📅 Révision {item['jalon']} décalée du {current_date.strftime('%Y-%m-%d')} au {new_date.strftime('%Y-%m-%d')}")

# === ENDPOINTS API ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de santé de l'API"""
    stats = json_manager.get_stats()
    return jsonify({
        "status": "healthy",
        "data_stats": stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/examens', methods=['GET'])
def get_examens():
    """Récupérer tous les examens"""
    examens = json_manager.get_examens()
    return jsonify(examens)

@app.route('/api/examens/<int:exam_id>', methods=['GET'])
def get_examen(exam_id):
    """Récupérer un examen spécifique"""
    examen = json_manager.get_examen(exam_id)
    if not examen:
        return jsonify({"error": "Examen non trouvé"}), 404
    return jsonify(examen)

@app.route('/api/examens', methods=['POST'])
def create_examen():
    """Créer un nouvel examen"""
    data = request.json
    if not data or 'titre' not in data or 'date_exam' not in data:
        return jsonify({"error": "Données manquantes"}), 400
    
    examen = json_manager.create_examen(data)
    return jsonify(examen), 201

@app.route('/api/examens/<int:exam_id>', methods=['PUT'])
def update_examen(exam_id):
    """Mettre à jour un examen"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    success = json_manager.update_examen(exam_id, data)
    if not success:
        return jsonify({"error": "Examen non trouvé"}), 404
    
    return jsonify({"message": "Examen mis à jour"})

@app.route('/api/examens/<int:exam_id>', methods=['DELETE'])
def delete_examen(exam_id):
    """Supprimer un examen"""
    success = json_manager.delete_examen(exam_id)
    if not success:
        return jsonify({"error": "Examen non trouvé"}), 404
    
    return jsonify({"message": "Examen supprimé"})

@app.route('/api/cours', methods=['GET'])
def get_cours():
    """Récupérer tous les cours ou ceux d'un examen spécifique"""
    examen_id = request.args.get('examen_id', type=int)
    cours = json_manager.get_cours(examen_id)
    
    # Enrichir les cours avec les informations des examens
    examens = json_manager.get_examens()
    examens_dict = {e['id']: e for e in examens}
    
    for course in cours:
        exam = examens_dict.get(course.get('examen_id'))
        if exam:
            course['examen_nom'] = exam.get('titre', 'Examen inconnu')
            course['date_exam'] = exam.get('date_exam')
    
    return jsonify(cours)

@app.route('/api/cours/<int:cours_id>', methods=['GET'])
def get_cours_by_id(cours_id):
    """Récupérer un cours spécifique"""
    cours = json_manager.get_cours_by_id(cours_id)
    if not cours:
        return jsonify({"error": "Cours non trouvé"}), 404
    return jsonify(cours)

@app.route('/api/cours', methods=['POST'])
def create_cours():
    """Créer un nouveau cours"""
    data = request.json
    if not data or 'titre' not in data or 'examen_id' not in data:
        return jsonify({"error": "Données manquantes"}), 400
    
    cours = json_manager.create_cours(data)
    
    # Générer automatiquement le planning pour ce cours
    regenerate_planning_for_exam(cours['examen_id'])
    
    return jsonify(cours), 201

@app.route('/api/cours/<int:cours_id>', methods=['PUT'])
def update_cours(cours_id):
    """Mettre à jour un cours"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    success = json_manager.update_cours(cours_id, data)
    if not success:
        return jsonify({"error": "Cours non trouvé"}), 404
    
    # Régénérer le planning
    cours = json_manager.get_cours_by_id(cours_id)
    if cours:
        regenerate_planning_for_exam(cours['examen_id'])
    
    return jsonify({"message": "Cours mis à jour"})

@app.route('/api/cours/<int:cours_id>', methods=['DELETE'])
def delete_cours(cours_id):
    """Supprimer un cours"""
    cours = json_manager.get_cours_by_id(cours_id)
    if not cours:
        return jsonify({"error": "Cours non trouvé"}), 404
    
    exam_id = cours['examen_id']
    success = json_manager.delete_cours(cours_id)
    
    # Régénérer le planning
    regenerate_planning_for_exam(exam_id)
    
    return jsonify({"message": "Cours supprimé"})

@app.route('/api/planning/consolidated', methods=['GET'])
def get_planning_consolidated():
    """Récupérer le planning consolidé avec informations des cours et examens"""
    planning = json_manager.get_planning()
    cours_list = json_manager.get_cours()
    examens_list = json_manager.get_examens()
    
    # Créer des dictionnaires pour un accès rapide
    cours_dict = {c['id']: c for c in cours_list}
    examens_dict = {e['id']: e for e in examens_list}
    
    # Enrichir le planning avec les informations des cours et examens
    consolidated = []
    for item in planning:
        if item.get('cours_id') and item.get('examen_id'):
            cours = cours_dict.get(item['cours_id'], {})
            examen = examens_dict.get(item['examen_id'], {})
            
            consolidated_item = {
                **item,
                'cours_nom': cours.get('titre', 'Cours inconnu'),
                'cours_id': item.get('cours_id'),
                'examen_nom': examen.get('titre', 'Examen inconnu'),
                'examen_id': item.get('examen_id')
            }
            consolidated.append(consolidated_item)
    
    return jsonify(consolidated)

@app.route('/api/planning/exam/<int:exam_id>', methods=['GET'])
def get_planning_for_exam(exam_id):
    """Récupérer le planning pour un examen spécifique"""
    planning = json_manager.get_planning(exam_id)
    return jsonify(planning)

@app.route('/api/planning/<int:planning_id>', methods=['PUT'])
def update_planning_item(planning_id):
    """Mettre à jour un élément de planning"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    success = json_manager.update_planning_item(planning_id, data)
    if not success:
        return jsonify({"error": "Élément de planning non trouvé"}), 404
    
    return jsonify({"message": "Planning mis à jour"})

@app.route('/api/planning/<int:exam_id>/rebalance', methods=['POST'])
def rebalance_planning_endpoint(exam_id):
    """Rééquilibrer le planning d'un examen"""
    print(f"🔄 Début du rééquilibrage pour l'examen {exam_id}")
    
    exam = json_manager.get_examen(exam_id)
    if not exam:
        print(f"❌ Examen {exam_id} non trouvé")
        return jsonify({"error": f"Examen {exam_id} non trouvé"}), 404
    
    print(f"📚 Examen trouvé: {exam.get('titre', 'Sans titre')}")
    
    params = load_params()
    print(f"⚙️ Paramètres chargés: nb_max_par_j={params.nb_max_par_j}, duree_max={params.duree_max}")
    
    result = rebalance_planning(exam_id, params)
    print(f"📊 Résultat du rééquilibrage: {result}")
    
    return jsonify(result)

@app.route('/api/planning/rebalance-global', methods=['POST'])
def rebalance_planning_global_endpoint():
    """Rééquilibrer le planning global (tous les examens)"""
    print(f"🌍 Début du rééquilibrage GLOBAL")
    
    params = load_params()
    print(f"⚙️ Paramètres chargés: nb_max_par_j={params.nb_max_par_j}, duree_max={params.default_daily_minutes}")
    
    result = rebalance_planning_global(params)
    print(f"📊 Résultat du rééquilibrage global: {result}")
    
    return jsonify(result)

@app.route('/api/planning/conflicts', methods=['GET'])
def get_planning_conflicts():
    """Récupérer les conflits de planning avec informations détaillées"""
    params = load_params()
    conflicts = detect_conflicts(params)
    
    # Enrichir avec les informations des examens
    examens_list = json_manager.get_examens()
    examens_dict = {e['id']: e for e in examens_list}
    
    enriched_conflicts = []
    for conflict in conflicts:
        # Récupérer les examens concernés par ce conflit
        planning = json_manager.get_planning()
        examens_concernes = set()
        
        for item in planning:
            if (item.get('date_finale') == conflict['date_finale'] and 
                item.get('statut') != 'Fait' and 
                item.get('examen_id')):
                examens_concernes.add(item['examen_id'])
        
        # Ajouter les noms des examens
        examens_noms = [examens_dict.get(eid, {}).get('titre', 'Examen inconnu') 
                       for eid in examens_concernes]
        
        enriched_conflict = {
            **conflict,
            'examens': list(examens_concernes),
            'examens_noms': examens_noms
        }
        enriched_conflicts.append(enriched_conflict)
    
    return jsonify(enriched_conflicts)

@app.route('/api/scores', methods=['GET'])
def get_scores():
    """Récupérer tous les scores ou ceux d'un cours spécifique"""
    cours_id = request.args.get('cours_id', type=int)
    scores = json_manager.get_scores(cours_id)
    return jsonify(scores)

@app.route('/api/scores', methods=['POST'])
def create_score():
    """Créer un score"""
    data = request.json
    
    # Validation des données requises
    required_fields = ['cours_id', 'jalon', 'score', 'total']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Champ requis manquant: {field}"}), 400
    
    # Conversion des types pour éviter les erreurs
    try:
        cours_id = int(data['cours_id'])
        jalon = int(data['jalon']) if isinstance(data['jalon'], (int, str)) and str(data['jalon']).isdigit() else data['jalon']
        score = int(data['score'])
        total = int(data['total'])
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Erreur de type de données: {str(e)}"}), 400
    
    # Valeur par défaut pour date_eval si non fournie
    date_eval = data.get('date_eval', datetime.now().strftime('%Y-%m-%d'))
    data['date_eval'] = date_eval
    
    # S'assurer que les données sont dans le bon format pour la sauvegarde
    data['cours_id'] = cours_id
    data['jalon'] = jalon
    data['score'] = score
    data['total'] = total
    
    score_result = json_manager.create_score(data)
    
    # Ajuster le planning selon le score (seulement si jalon est numérique)
    if isinstance(jalon, int):
        date_eval = data.get('date_eval')
        adjust_planning_with_score(cours_id, jalon, score, total, date_eval)
    
    return jsonify({"message": "Score créé avec succès", "score": score_result}), 201

@app.route('/api/parametres', methods=['GET'])
def get_parametres():
    """Récupérer tous les paramètres"""
    parametres = json_manager.get_parametres()
    # Si c'est déjà une liste, la retourner directement
    if isinstance(parametres, list):
        return jsonify(parametres)
    # Sinon, convertir le dict en liste
    return jsonify([{"cle": k, "valeur": v} for k, v in parametres.items()])

@app.route('/api/parametres/<key>', methods=['GET'])
def get_parametre(key):
    """Récupérer un paramètre spécifique"""
    valeur = json_manager.get_parametre(key)
    if valeur is None:
        return jsonify({"error": "Paramètre non trouvé"}), 404
    return jsonify({"cle": key, "valeur": valeur})

@app.route('/api/parametres/<key>', methods=['PUT'])
def update_parametre(key):
    """Mettre à jour un paramètre"""
    data = request.json
    if not data or 'valeur' not in data:
        return jsonify({"error": "Données manquantes"}), 400
    
    # Validation de la valeur selon le type de paramètre
    valeur = data['valeur']
    numeric_params = ['duree_min', 'duree_max', 'nb_max_par_j', 'nb_min_par_j', 'bonus_ok', 'bonus_fail', 'seuil_ok', 'seuil_fail', 'temps_pause']
    
    if key in numeric_params:
        try:
            valeur = int(valeur)
            if valeur < 0:
                return jsonify({"error": f"Valeur négative non autorisée pour {key}"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": f"Valeur numérique requise pour {key}"}), 400
    
    success = json_manager.update_parametre(key, valeur)
    if not success:
        return jsonify({"error": f"Paramètre '{key}' non trouvé"}), 404
    
    return jsonify({"message": "Paramètre mis à jour"})

@app.route('/api/bareme', methods=['GET'])
def get_bareme():
    """Récupérer le barème"""
    bareme = json_manager.get_bareme()
    return jsonify(bareme)

@app.route('/api/bareme', methods=['PUT'])
def update_bareme():
    """Mettre à jour le barème"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    # Validation des données
    for item in data:
        if 'indice' not in item or 'nb_revisions' not in item:
            return jsonify({"error": "Structure de barème invalide"}), 400
    
    json_manager.data['bareme'] = data
    json_manager._save_data()
    return jsonify({"message": "Barème mis à jour"})

@app.route('/api/disponibilites', methods=['GET'])
def get_disponibilites():
    """Récupérer les disponibilités"""
    disponibilites = json_manager.get_disponibilites()
    return jsonify(disponibilites)

@app.route('/api/disponibilites', methods=['PUT'])
def update_disponibilites():
    """Mettre à jour les disponibilités"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    success = json_manager.update_disponibilites(data)
    if not success:
        return jsonify({"error": "Erreur lors de la mise à jour"}), 500
    
    return jsonify({"message": "Disponibilités mises à jour"})

@app.route('/api/disponibilite/weekly')
def get_disponibilite_weekly():
    """Récupérer les disponibilités hebdomadaires"""
    disponibilites = json_manager.get_disponibilites()
    # Retourner les disponibilités hebdomadaires par défaut
    weekly = {}
    days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    for day in days:
        weekly[day] = {'disponible': True, 'heures': {'debut': '09:00', 'fin': '18:00'}}
    
    # Mettre à jour avec les données existantes
    for disp in disponibilites:
        if disp.get('type') == 'weekly' and disp.get('jour') in weekly:
            weekly[disp['jour']] = {
                'disponible': disp.get('disponible', True),
                'heures': disp.get('heures', {'debut': '09:00', 'fin': '18:00'})
            }
    
    return jsonify(weekly)

@app.route('/api/disponibilite/weekly/<day>', methods=['PUT'])
def update_disponibilite_weekly(day):
    """Modifier la disponibilité d'un jour de la semaine"""
    data = request.json
    if not data:
        return jsonify({"error": "Données manquantes"}), 400
    
    # Mettre à jour ou créer la disponibilité hebdomadaire
    disponibilites = json_manager.get_disponibilites()
    
    # Chercher si une disponibilité existe déjà pour ce jour
    updated = False
    for i, disp in enumerate(disponibilites):
        if disp.get('type') == 'weekly' and disp.get('jour') == day:
            disponibilites[i].update({
                'disponible': data.get('disponible', True),
                'heures': data.get('heures', {'debut': '09:00', 'fin': '18:00'})
            })
            updated = True
            break
    
    # Si pas trouvé, créer une nouvelle entrée
    if not updated:
        new_disp = {
            'id': json_manager.get_next_id('disponibilites'),
            'type': 'weekly',
            'jour': day,
            'disponible': data.get('disponible', True),
            'heures': data.get('heures', {'debut': '09:00', 'fin': '18:00'})
        }
        disponibilites.append(new_disp)
    
    json_manager.save_data('disponibilites', disponibilites)
    return jsonify({"message": f"Disponibilité du {day} mise à jour"})

# === NOUVEAUX ENDPOINTS D'IMPORT/EXPORT ===

@app.route('/api/export', methods=['GET'])
def export_data():
    """Exporter toutes les données au format JSON"""
    try:
        data = json_manager.export_data()
        return send_file(
            json_manager.json_file,
            as_attachment=True,
            download_name=f"revisioncam_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500

@app.route('/api/import', methods=['POST'])
def import_data():
    """Importer des données depuis un fichier JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Aucun fichier sélectionné"}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({"error": "Le fichier doit être au format JSON"}), 400
        
        data = json.load(file)
        success = json_manager.import_data(data)
        
        if success:
            return jsonify({"message": "Données importées avec succès"})
        else:
            return jsonify({"error": "Erreur lors de l'import des données"}), 500
            
    except json.JSONDecodeError:
        return jsonify({"error": "Fichier JSON invalide"}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'import: {str(e)}"}), 500

# === SERVIR LES FICHIERS FRONTEND ===

@app.route('/')
def index():
    """Page d'accueil (connexion)"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/test-frontend')
def test_frontend():
    """Test pour vérifier l'accès aux fichiers frontend"""
    try:
        return jsonify({
            "frontend_dir": str(FRONTEND_DIR),
            "frontend_exists": FRONTEND_DIR.exists(),
            "files": list(FRONTEND_DIR.glob("*.html")) if FRONTEND_DIR.exists() else [],
            "cours_html_exists": (FRONTEND_DIR / "cours.html").exists() if FRONTEND_DIR.exists() else False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth.js')
def serve_auth_js():
    """Servir spécifiquement auth.js avec le bon Content-Type"""
    response = send_from_directory(FRONTEND_DIR, 'auth.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/app.js')
def serve_app_js():
    """Servir spécifiquement app.js avec le bon Content-Type"""
    response = send_from_directory(FRONTEND_DIR, 'app.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/cours.html')
def serve_cours():
    """Servir la page cours"""
    return send_from_directory(FRONTEND_DIR, 'cours.html')

@app.route('/planning.html')
def serve_planning():
    """Servir la page planning"""
    return send_from_directory(FRONTEND_DIR, 'planning.html')

@app.route('/scores.html')
def serve_scores():
    """Servir la page scores"""
    return send_from_directory(FRONTEND_DIR, 'scores.html')

@app.route('/parametres.html')
def serve_parametres():
    """Servir la page paramètres"""
    return send_from_directory(FRONTEND_DIR, 'parametres.html')

@app.route('/login.html')
def serve_login():
    """Servir la page login"""
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/indexcardcamille.html')
def serve_indexcardcamille():
    """Servir la page indexcardcamille"""
    return send_from_directory(FRONTEND_DIR, 'indexcardcamille.html')

@app.route('/qcm.html')
def serve_qcm():
    """Servir la page qcm"""
    return send_from_directory(FRONTEND_DIR, 'qcm.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    """Servir les fichiers frontend (après les routes API et statiques)"""
    # Vérifier que le fichier existe
    file_path = FRONTEND_DIR / filename
    if file_path.exists() and file_path.is_file():
        # Définir le bon Content-Type pour les fichiers JS
        if filename.endswith('.js'):
            response = send_from_directory(FRONTEND_DIR, filename)
            response.headers['Content-Type'] = 'application/javascript'
            return response
        elif filename.endswith('.css'):
            response = send_from_directory(FRONTEND_DIR, filename)
            response.headers['Content-Type'] = 'text/css'
            return response
        else:
            return send_from_directory(FRONTEND_DIR, filename)
    else:
        # Si le fichier n'existe pas, rediriger vers index.html (pour SPA)
        return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir les fichiers statiques (compatibilité avec les anciennes références)"""
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/api/planning/logs', methods=['GET'])
def get_planning_logs():
    """Récupérer les logs de planning"""
    # Pour l'instant, retourner une liste vide car les logs ne sont pas encore implémentés
    return jsonify([])

if __name__ == '__main__':
    import os
    # Initialiser les données
    init_data()
    
    port = int(os.environ.get('PORT', 8080))
    print("🚀 Lancement de RevisionCam avec Flask et JSON...")
    print(f"📱 Accédez à l'application sur: http://localhost:{port}")
    print("🔐 Identifiants: camcam / 202122")
    print("📄 Base de données: revisioncam.json")
    
    app.run(host='0.0.0.0', port=port, debug=False)

