import datetime
import random
from django.db import models

from core.forum.models import Etudiant # Juste pour le type Hinting si tu veux


# La fonction de génération du matricule à l'intérieur de ton fichier models.py
# ou dans un fichier utilities.py si tu préfères
def generate_unique_matricule():
    """
    Génère un numéro matricule unique selon le format :
    AA/ucc/RRRR/AA+1/
    S'assure de l'unicité en vérifiant dans la base de données.
    """
    current_year = datetime.date.today().year
    previous_year_digits = str(current_year)[-2:]
    fixed_part = "ucc"
    next_year_digits = str(current_year + 1)[-2:]

    while True:
        random_digits = str(random.randint(0, 9999)).zfill(4)
        matricule = f"{previous_year_digits}/{fixed_part}/{random_digits}/{next_year_digits}/"
        # Vérifie si le matricule existe déjà dans la base de données
        if not Etudiant.objects.filter(matricule=matricule).exists():
            return matricule

