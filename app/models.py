from datetime import date
from typing import List

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Exam(Base):
    __tablename__ = "examens"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    date_exam = Column(Date, nullable=False)

    courses = relationship("Course", back_populates="exam", cascade="all, delete-orphan")
    planning_items = relationship("PlanningItem", back_populates="exam", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "cours"

    id = Column(Integer, primary_key=True, index=True)
    examen_id = Column(ForeignKey("examens.id"), nullable=False)
    titre = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "Majeur" or "Mineur"
    date_j0 = Column(Date, nullable=False)
    duree = Column(Integer, nullable=False)
    duree_estimee = Column(Integer, nullable=True)
    priorite_indice = Column(Integer, nullable=False, default=0)
    est_effectue = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True

    exam = relationship("Exam", back_populates="courses")
    scores = relationship("Score", back_populates="course", cascade="all, delete-orphan")
    planning_items = relationship("PlanningItem", back_populates="course", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    cours_id = Column(ForeignKey("cours.id"), nullable=False)
    jalon = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    date_eval = Column(Date, nullable=False)

    course = relationship("Course", back_populates="scores")


class PlanningItem(Base):
    __tablename__ = "planning"

    id = Column(Integer, primary_key=True, index=True)
    cours_id = Column(ForeignKey("cours.id"), nullable=False)
    examen_id = Column(ForeignKey("examens.id"), nullable=False)
    jalon = Column(String, nullable=False)
    date_prev = Column(Date, nullable=False)
    date_finale = Column(Date, nullable=False)
    duree = Column(Integer, nullable=False)
    statut = Column(String, nullable=False, default="À faire")
    est_effectue = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True

    course = relationship("Course", back_populates="planning_items")
    exam = relationship("Exam", back_populates="planning_items")


class Disponibilite(Base):
    __tablename__ = "disponibilite"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    dispo_min = Column(Integer, nullable=False)


class Bareme(Base):
    __tablename__ = "bareme"

    indice = Column(Integer, primary_key=True)
    nb_revisions = Column(Integer, nullable=False)


class Parametre(Base):
    __tablename__ = "parametres"

    cle = Column(String, primary_key=True)
    valeur = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
