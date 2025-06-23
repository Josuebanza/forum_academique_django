# main/models.py
import datetime
import random
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

class UserManager(BaseUserManager):
    def _create_user(self, email, password, profile_type, **extra_fields):
        if not email:
            raise ValueError("L'adresse email doit être renseignée")
        email = self.normalize_email(email)
        user = self.model(email=email, profile_type=profile_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, profile_type='etudiant', **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, profile_type, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        # Le superuser est un admin par défaut
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, 'admin', **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    PROFILE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('professeur', 'Professeur'),
        ('admin', 'Administrateur'),
    ]

    email = models.EmailField('Adresse e-mail', unique=True)
    first_name = models.CharField('Prénom', max_length=30, blank=True)
    last_name  = models.CharField('Nom',     max_length=30, blank=True)
    #date_naissance = models.DateField("date de naissance",blank=True)
    profile_type = models.CharField(
        'Type de profil',
        max_length=20,
        choices=PROFILE_CHOICES,
        default='etudiant',
        help_text="Rôle principal de l'utilisateur"
    )

    # champs Django « standard » pour gérer l’admin et la connexion
    is_active = models.BooleanField('Actif', default=True)
    is_staff  = models.BooleanField('Personnel', default=False)
    date_joined = models.DateTimeField('Date d\'inscription', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email + password sont obligatoires

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.email} ({self.get_profile_type_display()})"

    # Méthodes d’accès rapide
    def is_etudiant(self):
        return self.profile_type == 'etudiant'

    def is_professeur(self):
        return self.profile_type == 'professeur'

    def is_admin(self):
        return self.profile_type == 'admin' or self.is_superuser



class Faculte(models.Model):
    nom_fac = models.CharField(max_length=100)
    code_fac = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nom_fac


class Promotion(models.Model):
    nom_promo = models.CharField(max_length=50)
    code_promo = models.CharField(max_length=20, unique=True)
    id_faculte = models.ForeignKey(Faculte, on_delete=models.PROTECT, related_name='promotions')

    def __str__(self):
        return f"{self.nom_promo} ({self.code_promo})"


class Professeur(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prof_profile'
    )
    statut  = models.CharField(max_length=50)
    #email = models.EmailField("Email professionnel", unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.statut})"


class Cours(models.Model):
    titre_cours     = models.CharField(max_length=100)
    code_cours      = models.CharField(max_length=20, unique=True)
    id_professeur = models.ForeignKey(Professeur, on_delete=models.PROTECT, related_name='cours')

    def __str__(self):
        return f"{self.code_cours} – {self.titre_cours}"


class Travail(models.Model):
    titre_tp      = models.CharField("Titre du TP", max_length=200)
    date_limit = models.DateTimeField("Date limite")
    id_cours      = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='travaux')
    description = models.TextField("Description du TP", blank=True, null=True, default='')

    def __str__(self):
        return self.titre_tp


class GroupeDeTravail(models.Model):
    nom_groupe     = models.CharField(max_length=100)
    statut_groupe  = models.CharField(max_length=50)
    id_travail = models.ForeignKey(Travail, on_delete=models.CASCADE, related_name='groupes')

    def __str__(self):
        return self.nom_groupe


class Rapport(models.Model):
    id_groupe         = models.ForeignKey(GroupeDeTravail, on_delete=models.CASCADE, related_name='rapports')
    lien_fichier_rapport   = models.URLField("URL du rapport")
    date_soumission = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rapport {self.id} pour {self.id_groupe.nom_groupe}"



def generate_matricule():
    """
    Génère un numéro matricule unique selon le format :
    AA/ucc/RRRR/AA+1/

    - AA: Deux derniers chiffres de l'année d'inscription.
    - ucc: Chaîne de caractères fixe "ucc".
    - RRRR: Série de 4 chiffres aléatoires.
    - AA+1: Deux derniers chiffres de l'année suivant l'inscription.
    """
    current_year = datetime.date.today().year

    # 1. Deux derniers chiffres de l'année d'inscription (previous)
    previous_year_digits = str(current_year)[-2:]

    # 2. Partie fixe "ucc"
    fixed_part = "ucc"

    # 3. Série de 4 chiffres aléatoires (aléatoire)
    # Pour garantir une certaine unicité, on peut s'assurer qu'il a 4 chiffres.
    random_digits = str(random.randint(0, 9999)).zfill(4)

    # 4. Deux derniers chiffres de l'année suivant l'inscription (next)
    next_year_digits = str(current_year + 1)[-2:]

    # Construire le matricule final
    matricule = f"{previous_year_digits}/{fixed_part}/{random_digits}/{next_year_digits}"

    return matricule


class Etudiant(models.Model):
    matricule     = models.CharField("numéro matricule", max_length=14, unique=True, default=generate_matricule, primary_key=True,)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='etudiant_profile'
    )
    #nom_etudiant  = models.CharField(max_length=100)
    id_promotion  = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name='etudiants',null=True, blank=True)
    id_faculte    = models.ForeignKey(Faculte, on_delete=models.PROTECT, related_name='etudiants', null=True, blank=True)

    # inscription dans un groupes
    # id_groupe = models.ManyToManyField(GroupeDeTravail, through='Rejoindre groupe', related_name='etudiants')
    
    # def save(self, *args, **kwargs):
    #     if not self.matricule: # Génère le matricule seulement s'il n'existe pas déjà
    #         self.matricule = generate_matricule()
    #     super().save(*args, **kwargs)
    
    def __str__(self):
        return f" ({self.matricule}) - {self.id_promotion} - {self.user.first_name} {self.user.last_name}"


class SujetDiscussion(models.Model):
    titre_sujet = models.CharField("Titre du Sujet", max_length=200)
    date_creation  = models.DateTimeField("Date limite", auto_now_add=True)
    description = models.TextField("Description du sujet")
    id_createur = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='sujets')

    def __str__(self):
        return self.titre_sujet


class rejoundregroupe(models.Model):
    id_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    id_groupe    = models.ForeignKey(GroupeDeTravail, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('id_etudiant', 'id_groupe')

    def __str__(self):
        return f"{self.id_etudiant} → {self.id_groupe}"


class EtudiantGroupe(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    groupe   = models.ForeignKey(GroupeDeTravail, on_delete=models.CASCADE)
    est_chef = models.BooleanField("Chef de groupe", default=False)
    date_rejoindre = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('etudiant', 'groupe')

    def __str__(self):
        role = "Chef" if self.est_chef else "Membre"
        return f"{self.etudiant} ({role}) dans {self.groupe}"


class Contribution(models.Model):
    ETEXT = "texte"
    EFILE = "fichier"
    TYPES = [
        (ETEXT, 'Texte'),
        (EFILE, 'Fichier'),
    ]
    auteur   = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='contributions')
    type_contrib = models.CharField(max_length=20, choices=TYPES)
    contenu     = models.TextField()
    #legende     = models.CharField(max_length=255, blank=True)
    date_post   = models.DateTimeField(auto_now_add=True)
    fichier     = models.FileField(upload_to='contributions/', blank=True, null=True)
    id_travail = models.ForeignKey(Travail, on_delete=models.CASCADE, related_name='contributions')
    

    def __str__(self):
        return f"{self.get_type_contrib_display()} de {self.auteur} dans {self.id_travail}"


class Commentaire(models.Model):
    auteur    = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='commentaires')
    id_contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='commentaires')
    contenu_com     = models.TextField()
    date_com    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.auteur}"


class Reaction(models.Model):
    J_AIME = 'like'
    JE_DETESTE ='dislike'
    TYPES = [
        (J_AIME, 'J’aime'),
        (JE_DETESTE, 'Je n’aime pas'),
    ]
    etudiant    = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='reactions')
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='reactions')
    type_reaction = models.CharField(max_length=10, choices=TYPES)

    class Meta:
        unique_together = ('etudiant', 'contribution')

    def __str__(self):
        return f"{self.get_type_reaction_display()} par {self.etudiant}"
