from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.BaremeRead])
def list_bareme(db: Session = Depends(get_db)):
    return crud.get_bareme(db)


@router.put("/{indice}", response_model=schemas.BaremeRead)
def update_bareme(indice: int, payload: schemas.BaremeUpdate, db: Session = Depends(get_db)):
    if indice < 0 or indice > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Indice hors plage 0-10")
    if payload.nb_revisions <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nombre de révisions doit être positif")

    return crud.set_bareme(db, indice, payload.nb_revisions)
