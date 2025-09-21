from datetime import date
from typing import List

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Exam(Base):
    __tablename__ = "examens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titre: Mapped[str] = mapped_column(String, nullable=False)
    date_exam: Mapped[date] = mapped_column(Date, nullable=False)

    courses: Mapped[List["Course"]] = relationship("Course", back_populates="exam", cascade="all, delete-orphan")
    planning_items: Mapped[List["PlanningItem"]] = relationship("PlanningItem", back_populates="exam", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "cours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    examen_id: Mapped[int] = mapped_column(ForeignKey("examens.id"), nullable=False)
    titre: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # "Majeur" or "Mineur"
    date_j0: Mapped[date] = mapped_column(Date, nullable=False)
    duree: Mapped[int] = mapped_column(Integer, nullable=False)
    duree_estimee: Mapped[int] = mapped_column(Integer, nullable=True)
    priorite_indice: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    exam: Mapped[Exam] = relationship("Exam", back_populates="courses")
    scores: Mapped[List["Score"]] = relationship("Score", back_populates="course", cascade="all, delete-orphan")
    planning_items: Mapped[List["PlanningItem"]] = relationship("PlanningItem", back_populates="course", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cours_id: Mapped[int] = mapped_column(ForeignKey("cours.id"), nullable=False)
    jalon: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    date_eval: Mapped[date] = mapped_column(Date, nullable=False)

    course: Mapped[Course] = relationship("Course", back_populates="scores")


class PlanningItem(Base):
    __tablename__ = "planning"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cours_id: Mapped[int] = mapped_column(ForeignKey("cours.id"), nullable=False)
    examen_id: Mapped[int] = mapped_column(ForeignKey("examens.id"), nullable=False)
    jalon: Mapped[str] = mapped_column(String, nullable=False)
    date_prev: Mapped[date] = mapped_column(Date, nullable=False)
    date_finale: Mapped[date] = mapped_column(Date, nullable=False)
    duree: Mapped[int] = mapped_column(Integer, nullable=False)
    statut: Mapped[str] = mapped_column(String, nullable=False, default="À faire")

    course: Mapped[Course] = relationship("Course", back_populates="planning_items")
    exam: Mapped[Exam] = relationship("Exam", back_populates="planning_items")


class Disponibilite(Base):
    __tablename__ = "disponibilite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    dispo_min: Mapped[int] = mapped_column(Integer, nullable=False)


class Bareme(Base):
    __tablename__ = "bareme"

    indice: Mapped[int] = mapped_column(Integer, primary_key=True)
    nb_revisions: Mapped[int] = mapped_column(Integer, nullable=False)


class Parametre(Base):
    __tablename__ = "parametres"

    cle: Mapped[str] = mapped_column(String, primary_key=True)
    valeur: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
