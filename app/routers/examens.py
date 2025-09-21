from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.ExamRead, status_code=status.HTTP_201_CREATED)
def create_exam(exam: schemas.ExamCreate, db: Session = Depends(get_db)):
    return crud.create_exam(db, exam)


@router.get("/", response_model=list[schemas.ExamRead])
def list_examens(db: Session = Depends(get_db)):
    return crud.list_examens(db)


@router.get("/{exam_id}", response_model=schemas.ExamRead)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen introuvable")
    
    # Supprimer l'examen (cascade automatique pour les cours et planning)
    db.delete(exam)
    db.commit()
    return None
