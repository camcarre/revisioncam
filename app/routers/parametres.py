from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.ParametreRead])
def list_parametres(db: Session = Depends(get_db)):
    return crud.get_parametres(db)


@router.put("/{cle}", response_model=schemas.ParametreRead)
def update_parametre(cle: str, payload: schemas.ParametreUpdate, db: Session = Depends(get_db)):
    # Certains paramètres peuvent être négatifs (comme bonus_fail)
    # On valide seulement que la valeur est un nombre valide
    if not isinstance(payload.valeur, (int, float)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La valeur doit être un nombre")

    updated = crud.set_parametre(db, cle, payload.valeur, payload.description)
    return updated
