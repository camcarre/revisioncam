from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models, schemas


# Exams

def create_exam(db: Session, exam: schemas.ExamCreate) -> models.Exam:
    db_exam = models.Exam(**exam.model_dump())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


def list_examens(db: Session) -> list[models.Exam]:
    return db.query(models.Exam).all()


def get_exam(db: Session, exam_id: int) -> Optional[models.Exam]:
    return db.get(models.Exam, exam_id)


# Courses

def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def list_courses_by_exam(db: Session, exam_id: int) -> list[models.Course]:
    return db.query(models.Course).filter(models.Course.examen_id == exam_id).all()


def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.get(models.Course, course_id)


def update_course(db: Session, course_id: int, course_in: schemas.CourseCreate) -> models.Course:
    db_course = get_course(db, course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    
    # Mettre à jour les champs
    for field, value in course_in.dict(exclude_unset=True).items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


# Scores

def create_score(db: Session, score: schemas.ScoreCreate) -> models.Score:
    db_score = models.Score(**score.model_dump())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


def list_scores_for_course(db: Session, course_id: int) -> list[models.Score]:
    return db.query(models.Score).filter(models.Score.cours_id == course_id).all()


# Planning

def add_planning_items(db: Session, items: Iterable[models.PlanningItem]) -> list[models.PlanningItem]:
    buffered = list(items)
    db.add_all(buffered)
    db.commit()
    for item in buffered:
        db.refresh(item)
    return buffered


def upsert_planning_item(db: Session, item: models.PlanningItem) -> models.PlanningItem:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_planning_by_date(db: Session, target_date: date) -> list[models.PlanningItem]:
    return db.query(models.PlanningItem).filter(
        models.PlanningItem.date_finale == target_date
    ).all()


def list_planning_by_exam(db: Session, exam_id: int) -> list[models.PlanningItem]:
    return db.query(models.PlanningItem).filter(
        models.PlanningItem.examen_id == exam_id
    ).all()


def get_planning_item(db: Session, item_id: int) -> Optional[models.PlanningItem]:
    return db.get(models.PlanningItem, item_id)


def save_planning_item(db: Session, item: models.PlanningItem) -> models.PlanningItem:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_planning_for_course_jalon(db: Session, course_id: int, jalon: str) -> Optional[models.PlanningItem]:
    return db.query(models.PlanningItem).filter(
        and_(models.PlanningItem.cours_id == course_id, models.PlanningItem.jalon == jalon)
    ).first()


def delete_planning_for_course(db: Session, course_id: int) -> None:
    items = db.query(models.PlanningItem).filter(models.PlanningItem.cours_id == course_id).all()
    for item in items:
        db.delete(item)
    db.commit()


# Disponibilite

def get_disponibilite_for_date(db: Session, target_date: date) -> Optional[models.Disponibilite]:
    return db.query(models.Disponibilite).filter(models.Disponibilite.date == target_date).first()


def upsert_disponibilite(db: Session, dispo: schemas.DisponibiliteCreate) -> models.Disponibilite:
    existing = get_disponibilite_for_date(db, dispo.date)
    if existing:
        existing.dispo_min = dispo.dispo_min
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    new_dispo = models.Disponibilite(**dispo.model_dump())
    db.add(new_dispo)
    db.commit()
    db.refresh(new_dispo)
    return new_dispo


# Bareme

def get_bareme(db: Session) -> list[models.Bareme]:
    return db.query(models.Bareme).order_by(models.Bareme.indice).all()


def get_bareme_by_indice(db: Session, indice: int) -> Optional[models.Bareme]:
    return db.get(models.Bareme, indice)


def set_bareme(db: Session, indice: int, nb_revisions: int) -> models.Bareme:
    entry = get_bareme_by_indice(db, indice)
    if entry is None:
        entry = models.Bareme(indice=indice, nb_revisions=nb_revisions)
    else:
        entry.nb_revisions = nb_revisions
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# Parametres

def get_parametres(db: Session) -> list[models.Parametre]:
    return db.query(models.Parametre).all()


def get_parametre(db: Session, cle: str) -> Optional[models.Parametre]:
    return db.get(models.Parametre, cle)


def set_parametre(db: Session, cle: str, valeur: int, description: Optional[str] = None) -> models.Parametre:
    entry = get_parametre(db, cle)
    if entry is None:
        entry = models.Parametre(cle=cle, valeur=valeur, description=description)
    else:
        entry.valeur = valeur
        if description is not None:
            entry.description = description
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def list_disponibilites(db: Session) -> list[models.Disponibilite]:
    return db.query(models.Disponibilite).all()

def list_planning_for_course(db: Session, course_id: int) -> list[models.PlanningItem]:
    return db.query(models.PlanningItem).filter(
        models.PlanningItem.cours_id == course_id
    ).all()


def add_planning_items(db: Session, planning_items: list[models.PlanningItem]) -> list[models.PlanningItem]:
    """Ajoute plusieurs items de planning à la base de données."""
    for item in planning_items:
        db.add(item)
    db.commit()
    
    # Rafraîchir tous les items pour obtenir leurs IDs
    for item in planning_items:
        db.refresh(item)
    
    return planning_items
