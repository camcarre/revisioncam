from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, planning_service, schemas
from ..database import get_db

router = APIRouter()


@router.get("/date/{target_date}", response_model=list[schemas.PlanningItemRead])
def planning_for_day(target_date: date, db: Session = Depends(get_db)):
    return crud.list_planning_by_date(db, target_date)


@router.get("/exam/{exam_id}", response_model=list[schemas.PlanningItemRead])
def planning_for_exam(exam_id: int, db: Session = Depends(get_db)):
    return crud.list_planning_by_exam(db, exam_id)


@router.put("/{item_id}", response_model=schemas.PlanningItemRead)
def update_planning_item(item_id: int, update: schemas.PlanningItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_planning_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Élément de planning introuvable")

    if update.statut is not None:
        item.statut = update.statut
    if update.date_finale is not None:
        item.date_finale = update.date_finale

    return crud.save_planning_item(db, item)


@router.post("/generate/{exam_id}", response_model=list[schemas.PlanningItemRead])
def generate_planning_for_exam(exam_id: int, db: Session = Depends(get_db)):
    """Génère le planning pour tous les cours d'un examen"""
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")
    
    # Supprimer l'ancien planning pour cet examen
    existing_planning = crud.list_planning_by_exam(db, exam_id)
    for item in existing_planning:
        db.delete(item)
    db.commit()
    
    # Générer le planning pour chaque cours
    courses = crud.list_courses_by_exam(db, exam_id)
    all_planning_items = []
    
    for course in courses:
        planning_items = planning_service.generate_planning_for_course(db, course)
        saved_items = crud.add_planning_items(db, planning_items)
        all_planning_items.extend(saved_items)
    
    return all_planning_items
