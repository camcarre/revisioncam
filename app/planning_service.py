from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from . import crud, models

# Default spacing offsets (days after J0)
OFFSETS_TEMPLATE = [1, 3, 7, 14, 21, 30, 45, 60, 75, 90, 105, 120, 135]
# Default duration factors (percentage of initial duration)
DURATION_FACTORS = [0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.15, 0.1, 0.1]


@dataclass
class PlanningParams:
    duree_min: int
    duree_max: int
    nb_max_par_j: int
    default_daily_minutes: int


@dataclass
class DayState:
    total_duration: int
    count: int


def _load_params(db: Session) -> PlanningParams:
    duree_min = crud.get_parametre(db, "duree_min").valeur  # defaults ensured at startup
    duree_max = crud.get_parametre(db, "duree_max").valeur
    nb_max_par_j = crud.get_parametre(db, "nb_max_par_j").valeur
    default_daily_minutes = nb_max_par_j * duree_max
    return PlanningParams(duree_min=duree_min, duree_max=duree_max, nb_max_par_j=nb_max_par_j, default_daily_minutes=default_daily_minutes)


def _load_availability(db: Session) -> Dict[date, int]:
    return {dispo.date: dispo.dispo_min for dispo in crud.list_disponibilites(db)}


def _build_daily_state(planning_items: List[models.PlanningItem]) -> Dict[date, DayState]:
    state: Dict[date, DayState] = {}
    for item in planning_items:
        day_state = state.setdefault(item.date_finale, DayState(total_duration=0, count=0))
        day_state.total_duration += item.duree
        day_state.count += 1
    return state


def _get_nb_revisions(db: Session, indice: int) -> int:
    bareme = crud.get_bareme_by_indice(db, indice)
    if bareme is None:
        # fall back to medium workload
        return 3
    return max(1, bareme.nb_revisions)


def _compute_offsets(nb_revisions: int, total_days: int) -> List[int]:
    if total_days <= 0:
        return [0] * nb_revisions

    offsets: List[int] = []
    template_idx = 0
    last_offset = 0
    max_offset = max(1, total_days - 1)

    while len(offsets) < nb_revisions:
        if template_idx < len(OFFSETS_TEMPLATE):
            candidate = OFFSETS_TEMPLATE[template_idx]
            template_idx += 1
        else:
            candidate = last_offset + 15

        candidate = min(candidate, max_offset)
        if candidate <= last_offset:
            candidate = min(max_offset, last_offset + 1)
        offsets.append(candidate)
        last_offset = candidate

    return offsets


def _compute_duration(base_duration: int, params: PlanningParams, index: int) -> int:
    factor = DURATION_FACTORS[index] if index < len(DURATION_FACTORS) else DURATION_FACTORS[-1]
    estimated = int(round(base_duration * factor))
    return max(params.duree_min, min(params.duree_max, estimated))


def _is_flexible(course: models.Course) -> bool:
    if course.type.lower() == "majeur":
        return False
    return course.priorite_indice < 7


def _availability_for_day(availability_map: Dict[date, int], params: PlanningParams, target_date: date) -> int:
    return availability_map.get(target_date, params.default_daily_minutes)


def _find_slot(
    base_date: date,
    exam_date: date,
    duration: int,
    course: models.Course,
    params: PlanningParams,
    availability_map: Dict[date, int],
    daily_state: Dict[date, DayState],
) -> date:
    protect = not _is_flexible(course)
    candidate = base_date

    if candidate >= exam_date:
        candidate = exam_date - timedelta(days=1)

    while candidate < exam_date:
        state = daily_state.get(candidate, DayState(total_duration=0, count=0))
        availability = _availability_for_day(availability_map, params, candidate)

        if protect:
            break  # keep initial candidate even if it exceeds limits

        if state.count < params.nb_max_par_j and state.total_duration + duration <= availability:
            break

        candidate += timedelta(days=1)

    if candidate >= exam_date:
        candidate = exam_date - timedelta(days=1)

    return candidate


def _register_day(daily_state: Dict[date, DayState], target_date: date, duration: int) -> None:
    day_state = daily_state.get(target_date)
    if day_state is None:
        daily_state[target_date] = DayState(total_duration=duration, count=1)
    else:
        day_state.total_duration += duration
        day_state.count += 1


def regenerate_planning_for_exam(db: Session, exam_id: int) -> List[models.PlanningItem]:
    """
    Recalcule complètement le planning pour tous les cours d'un examen.
    Supprime l'ancien planning et génère un nouveau planning optimisé.
    """
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        return []
    
    # Supprimer tous les anciens items de planning pour cet examen
    existing_items = crud.list_planning_by_exam(db, exam_id)
    for item in existing_items:
        db.delete(item)
    db.commit()
    
    # Charger tous les cours de cet examen
    courses = crud.list_courses_by_exam(db, exam_id)
    if not courses:
        return []
    
    # Charger les paramètres et disponibilités une seule fois
    params = _load_params(db)
    availability_map = _load_availability(db)
    
    # Trier les cours par priorité (indice décroissant) pour traiter les plus importants en premier
    courses.sort(key=lambda c: c.priorite_indice, reverse=True)
    
    all_planning_items: List[models.PlanningItem] = []
    daily_state: Dict[date, DayState] = {}
    
    # Générer le planning pour chaque cours en tenant compte des autres
    for course in courses:
        course_items = _generate_planning_for_course_optimized(
            db, course, params, availability_map, daily_state, exam
        )
        all_planning_items.extend(course_items)
        
        # Mettre à jour l'état quotidien avec les nouveaux items
        for item in course_items:
            _register_day(daily_state, item.date_finale, item.duree)
    
    return all_planning_items


def _generate_planning_for_course_optimized(
    db: Session,
    course: models.Course,
    params: PlanningParams,
    availability_map: Dict[date, int],
    daily_state: Dict[date, DayState],
    exam: models.Exam
) -> List[models.PlanningItem]:
    """Version optimisée qui utilise l'état quotidien partagé entre tous les cours."""
    nb_revisions = _get_nb_revisions(db, course.priorite_indice)
    total_days = (exam.date_exam - course.date_j0).days if exam else 0
    offsets = _compute_offsets(nb_revisions, total_days)

    base_duration = course.duree_estimee or course.duree
    if base_duration <= 0:
        base_duration = params.duree_min

    items: List[models.PlanningItem] = []
    last_base_date: Optional[date] = None

    for idx, offset in enumerate(offsets):
        jalon_label = f"J{offset}" if offset > 0 else "J0"
        base_date = course.date_j0 + timedelta(days=offset)
        if exam and base_date >= exam.date_exam:
            base_date = exam.date_exam - timedelta(days=1)
        if last_base_date and base_date <= last_base_date:
            base_date = last_base_date + timedelta(days=1)
        if exam and base_date >= exam.date_exam:
            base_date = exam.date_exam - timedelta(days=1)
        if base_date < course.date_j0:
            base_date = course.date_j0

        duration = _compute_duration(base_duration, params, idx)
        final_date = _find_slot(base_date, exam.date_exam, duration, course, params, availability_map, daily_state)

        item = models.PlanningItem(
            cours_id=course.id,
            examen_id=course.examen_id,
            jalon=jalon_label,
            date_prev=base_date,
            date_finale=final_date,
            duree=duration,
            statut="À faire",
        )
        items.append(item)
        last_base_date = base_date

    return items


def generate_planning_for_course(db: Session, course: models.Course) -> List[models.PlanningItem]:
    exam = course.exam
    params = _load_params(db)
    availability_map = _load_availability(db)
    existing_items = []
    if exam is not None:
        existing_items = crud.list_planning_by_exam(db, exam.id)
    daily_state = _build_daily_state(existing_items)

    nb_revisions = _get_nb_revisions(db, course.priorite_indice)
    total_days = (exam.date_exam - course.date_j0).days if exam else 0
    offsets = _compute_offsets(nb_revisions, total_days)

    base_duration = course.duree_estimee or course.duree
    if base_duration <= 0:
        base_duration = params.duree_min

    items: List[models.PlanningItem] = []
    last_base_date: Optional[date] = None

    for idx, offset in enumerate(offsets):
        jalon_label = f"J{offset}" if offset > 0 else "J0"
        base_date = course.date_j0 + timedelta(days=offset)
        if exam and base_date >= exam.date_exam:
            base_date = exam.date_exam - timedelta(days=1)
        if last_base_date and base_date <= last_base_date:
            base_date = last_base_date + timedelta(days=1)
        if exam and base_date >= exam.date_exam:
            base_date = exam.date_exam - timedelta(days=1)
        if base_date < course.date_j0:
            base_date = course.date_j0

        duration = _compute_duration(base_duration, params, idx)
        final_date = _find_slot(base_date, exam.date_exam, duration, course, params, availability_map, daily_state)
        _register_day(daily_state, final_date, duration)

        item = models.PlanningItem(
            cours_id=course.id,
            examen_id=course.examen_id,
            jalon=jalon_label,
            date_prev=base_date,
            date_finale=final_date,
            duree=duration,
            statut="À faire",
        )
        items.append(item)
        last_base_date = base_date

    return items


def add_extra_revision_after_score(db: Session, score: models.Score) -> models.PlanningItem | None:
    course = score.course
    exam = course.exam
    params = _load_params(db)
    availability_map = _load_availability(db)
    daily_state = _build_daily_state(crud.list_planning_by_exam(db, exam.id))

    planning_items = sorted(
        crud.list_planning_for_course(db, course.id),
        key=lambda item: (item.date_finale, item.id),
    )

    if not planning_items:
        return None

    base_date = score.date_eval + timedelta(days=2)
    if base_date >= exam.date_exam:
        base_date = exam.date_exam - timedelta(days=1)

    duration = _compute_duration(course.duree_estimee or course.duree, params, len(planning_items))
    final_date = _find_slot(base_date, exam.date_exam, duration, course, params, availability_map, daily_state)
    _register_day(daily_state, final_date, duration)

    jalon_label = f"JR{score.id}"

    new_item = models.PlanningItem(
        cours_id=course.id,
        examen_id=course.examen_id,
        jalon=jalon_label,
        date_prev=base_date,
        date_finale=final_date,
        duree=duration,
        statut="À faire",
    )

    crud.save_planning_item(db, new_item)
    return new_item


def adjust_planning_after_high_score(db: Session, score: models.Score) -> None:
    course = score.course
    exam = course.exam

    planning_items = sorted(
        crud.list_planning_for_course(db, course.id),
        key=lambda item: (item.date_finale, item.id),
    )

    target_index = next((i for i, item in enumerate(planning_items) if item.jalon == score.jalon), None)
    if target_index is None:
        return

    if target_index + 1 >= len(planning_items):
        return  # nothing to space

    next_item = planning_items[target_index + 1]
    is_last = target_index + 1 == len(planning_items) - 1

    if is_last:
        final_anchor = exam.date_exam - timedelta(days=1)
        next_item.date_finale = min(next_item.date_finale, final_anchor)
        crud.save_planning_item(db, next_item)
        return

    following_item = planning_items[target_index + 2]
    suggested_date = next_item.date_finale + timedelta(days=2)
    max_allowed = following_item.date_finale - timedelta(days=1)
    new_date = min(suggested_date, max_allowed)
    if new_date <= next_item.date_finale:
        return

    next_item.date_finale = new_date
    crud.save_planning_item(db, next_item)
