from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.DisponibiliteRead])
def list_disponibilites(db: Session = Depends(get_db)):
    return crud.list_disponibilites(db)


@router.put("/", response_model=list[schemas.DisponibiliteRead])
def upsert_disponibilites(dispos: list[schemas.DisponibiliteCreate], db: Session = Depends(get_db)):
    """Met à jour plusieurs disponibilités en une fois"""
    results = []
    for dispo in dispos:
        if dispo.dispo_min < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La disponibilité ne peut pas être négative")
        result = crud.upsert_disponibilite(db, dispo)
        results.append(result)
    return results


@router.put("/single", response_model=schemas.DisponibiliteRead)
def upsert_single_disponibilite(dispo: schemas.DisponibiliteCreate, db: Session = Depends(get_db)):
    """Met à jour une seule disponibilité (pour compatibilité)"""
    if dispo.dispo_min <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La disponibilité doit être positive")
    return crud.upsert_disponibilite(db, dispo)


# Endpoints pour les disponibilités hebdomadaires (stockées temporairement en mémoire)
weekly_availability_store = {
    'lundi': 240,
    'mardi': 180,
    'mercredi': 300,
    'jeudi': 120,
    'vendredi': 240,
    'samedi': 180,
    'dimanche': 300
}

@router.get("/weekly", response_model=dict[str, int])
def get_weekly_availability():
    """Récupère les disponibilités hebdomadaires"""
    return weekly_availability_store

@router.put("/weekly/{jour}", response_model=dict[str, int])
def update_weekly_availability(jour: str, update: schemas.WeeklyAvailabilityUpdate):
    """Met à jour la disponibilité d'un jour de la semaine"""
    if jour not in weekly_availability_store:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jour invalide")
    
    # Validation de la valeur
    if update.dispo_min < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La disponibilité ne peut pas être négative")
    
    if update.dispo_min > 1440:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La disponibilité ne peut pas dépasser 1440 minutes (24h)")
    
    weekly_availability_store[jour] = update.dispo_min
    return weekly_availability_store
