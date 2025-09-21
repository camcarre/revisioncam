from sqlalchemy.orm import Session

from . import crud

DEFAULT_PARAMETRES = {
    "duree_min": (30, "Durée minimale d'une révision (minutes)"),
    "duree_max": (70, "Durée maximale d'une révision (minutes)"),
    "nb_max_par_j": (5, "Nombre maximum de révisions par jour"),
    "nb_min_par_j": (1, "Nombre minimum de révisions par jour (sauf jour off)"),
    "temps_pause": (10, "Pause entre deux séances (optionnel mais pratique)"),
    "seuil_fail": (60, "En dessous → rapprocher la prochaine révision"),
    "seuil_ok": (85, "Au-dessus → espacer la prochaine révision"),
    "bonus_fail": (-2, "Décalage appliqué si score < seuil_fail"),
    "bonus_ok": (2, "Décalage appliqué si score > seuil_ok"),
}

DEFAULT_BAREME = {
    0: 2,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
}


def ensure_defaults(db: Session) -> None:
    existing_params = {param.cle for param in crud.get_parametres(db)}
    for cle, (valeur, description) in DEFAULT_PARAMETRES.items():
        if cle not in existing_params:
            crud.set_parametre(db, cle=cle, valeur=valeur, description=description)

    existing_indices = {item.indice for item in crud.get_bareme(db)}
    for indice, nb in DEFAULT_BAREME.items():
        if indice not in existing_indices:
            crud.set_bareme(db, indice=indice, nb_revisions=nb)
