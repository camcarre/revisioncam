from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, planning_service, schemas
from ..database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.CourseWithPlanning, status_code=status.HTTP_201_CREATED)
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, course_in.examen_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")

    # Créer le cours
    db_course = crud.create_course(db, course_in)
    
    # Recalculer complètement le planning pour tout l'examen
    planning_items = planning_service.regenerate_planning_for_exam(db, course_in.examen_id)
    
    # Sauvegarder tous les items de planning
    saved_items = crud.add_planning_items(db, planning_items)

    return {"course": db_course, "planning": saved_items}


@router.get("/{exam_id}", response_model=list[schemas.CourseRead])
def list_courses(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")
    return crud.list_courses_by_exam(db, exam_id)


@router.put("/{course_id}", response_model=schemas.CourseWithPlanning)
def update_course(course_id: int, course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    # Vérifier que le cours existe
    db_course = crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
    
    # Vérifier que l'examen existe
    exam = crud.get_exam(db, course_in.examen_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")

    # Sauvegarder l'ancien examen_id pour le recalcul
    old_exam_id = db_course.examen_id

    # Mettre à jour le cours
    updated_course = crud.update_course(db, course_id, course_in)
    
    # Recalculer le planning pour l'ancien examen (si différent)
    if old_exam_id != course_in.examen_id:
        planning_items_old = planning_service.regenerate_planning_for_exam(db, old_exam_id)
        crud.add_planning_items(db, planning_items_old)
    
    # Recalculer le planning pour le nouvel examen
    planning_items = planning_service.regenerate_planning_for_exam(db, course_in.examen_id)
    saved_items = crud.add_planning_items(db, planning_items)

    return {"course": updated_course, "planning": saved_items}
