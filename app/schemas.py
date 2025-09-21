from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExamBase(BaseModel):
    titre: str
    date_exam: date


class ExamCreate(ExamBase):
    pass


class ExamRead(ExamBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    examen_id: int
    titre: str
    type: str = Field(pattern="^(Majeur|Mineur)$")
    date_j0: date
    duree: int = Field(gt=0, description="Durée en minutes, doit être positive")
    duree_estimee: Optional[int] = Field(default=None, description="Durée estimée en minutes")
    priorite_indice: int = Field(ge=0, le=10)


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ScoreBase(BaseModel):
    cours_id: int
    jalon: str
    score: int = Field(ge=0, description="Score obtenu, doit être positif")
    total: int = Field(gt=0, description="Score total, doit être positif")
    date_eval: date
    
    @model_validator(mode='after')
    def validate_score_not_exceed_total(self):
        if self.score > self.total:
            raise ValueError('Le score ne peut pas dépasser le total')
        return self


class ScoreCreate(ScoreBase):
    pass


class ScoreRead(ScoreBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PlanningItemBase(BaseModel):
    cours_id: int
    examen_id: int
    jalon: str
    date_prev: date
    date_finale: date
    duree: int
    statut: str


class PlanningItemUpdate(BaseModel):
    statut: Optional[str] = None
    date_finale: Optional[date] = None


class PlanningItemRead(PlanningItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DisponibiliteBase(BaseModel):
    date: date
    dispo_min: int


class DisponibiliteCreate(DisponibiliteBase):
    pass


class DisponibiliteRead(DisponibiliteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class WeeklyAvailabilityBase(BaseModel):
    jour: str = Field(pattern="^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)$")
    dispo_min: int = Field(ge=0, le=1440, description="Disponibilité en minutes (0-1440)")


class WeeklyAvailabilityCreate(WeeklyAvailabilityBase):
    pass


class WeeklyAvailabilityRead(WeeklyAvailabilityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class WeeklyAvailabilityUpdate(BaseModel):
    dispo_min: int = Field(ge=0, le=1440, description="Disponibilité en minutes (0-1440)")


class BaremeBase(BaseModel):
    nb_revisions: int


class BaremeUpdate(BaremeBase):
    pass


class BaremeRead(BaremeBase):
    indice: int

    model_config = ConfigDict(from_attributes=True)


class ParametreBase(BaseModel):
    valeur: int
    description: Optional[str] = None


class ParametreUpdate(ParametreBase):
    pass


class ParametreRead(ParametreBase):
    cle: str

    model_config = ConfigDict(from_attributes=True)


class CourseWithPlanning(BaseModel):
    course: CourseRead
    planning: list[PlanningItemRead]


class ScoreWithPlanning(BaseModel):
    score: ScoreRead
    course_planning: list[PlanningItemRead]
