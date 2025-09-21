from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, planning_service, schemas
from ..database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.ScoreWithPlanning, status_code=status.HTTP_201_CREATED)
def add_score(score_in: schemas.ScoreCreate, db: Session = Depends(get_db)):
    if score_in.total <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le total de questions doit être supérieur à 0")

    course = crud.get_course(db, score_in.cours_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")

    db_score = crud.create_score(db, score_in)
    ratio = db_score.score / db_score.total

    if ratio < 0.6:
        planning_service.add_extra_revision_after_score(db, db_score)
    elif ratio >= 0.85:
        planning_service.adjust_planning_after_high_score(db, db_score)

    updated_planning = crud.list_planning_for_course(db, score_in.cours_id)
    return {"score": db_score, "course_planning": updated_planning}
