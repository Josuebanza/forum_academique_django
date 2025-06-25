# main/forms.py
from django.contrib.auth import get_user_model
from django import forms
from .models import (
    EtudiantGroupe,
    GroupeDeTravail,
    Professeur,
    Promotion,
    SujetDiscussion,
    User,
    Etudiant,
    Travail,
    Rapport,
    Contribution,
    Commentaire,
    Cours,  # Ajout de l'import du modèle Cours
)

User = get_user_model()
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer mot de passe", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'profile_type')

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()  # ⚠️ Ceci déclenche le signal et crée le profil
        return user


class TravailForm(forms.ModelForm):
    class Meta:
        model = Travail
        fields = ['titre_tp', 'date_limit', 'id_cours']
        widgets = {
            'date_limit': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'cours': forms.Select(attrs={'class': 'form-select'}),
        }


class SujetDiscussionForm(forms.ModelForm):
    class Meta:
        model = SujetDiscussion
        fields = ['titre_sujet', 'description', 'id_createur']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4}),
            'id_createur': forms.Select(attrs={'class': 'form-select'}),
        }


class RapportForm(forms.ModelForm):
    class Meta:
        model = Rapport
        fields = ['lien_fichier_rapport', 'id_groupe']
        widgets = {
            'lien_fichier_rapport': forms.ClearableFileInput(),
        }


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['type_contrib','contenu','fichier']


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu_com']
        widgets = {'contenu_com': forms.Textarea(attrs={'rows':2})}


class JoindreGroupeForm(forms.ModelForm):
    # ... (Votre formulaire JoindreGroupeForm existant) ...
    groupe = forms.ModelChoiceField(
        queryset=GroupeDeTravail.objects.none(),
        label="Sélectionnez un groupe",
        help_text="Choisissez un groupe de travail pour ce TP."
    )

    class Meta:
        model = EtudiantGroupe
        fields = ['groupe']

    def __init__(self, *args, **kwargs):
        self.travail = kwargs.pop('travail', None)
        self.etudiant_instance = kwargs.pop('etudiant_instance', None)
        super().__init__(*args, **kwargs)

        if self.travail:
            self.fields['groupe'].queryset = GroupeDeTravail.objects.filter(id_travail=self.travail)
        else:
            self.fields['groupe'].queryset = GroupeDeTravail.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        groupe = cleaned_data.get('groupe')

        if self.etudiant_instance and groupe:
            if EtudiantGroupe.objects.filter(etudiant=self.etudiant_instance, groupe=groupe).exists():
                raise forms.ValidationError("Vous êtes déjà membre de ce groupe.")
        return cleaned_data

    def save(self, commit=True):
        etudiant_groupe = super().save(commit=False)
        etudiant_groupe.etudiant = self.etudiant_instance
        if commit:
            etudiant_groupe.save()
        return etudiant_groupe


class ContributionForm(forms.ModelForm):
    """
    Formulaire pour ajouter une nouvelle contribution à un travail.
    """
    class Meta:
        model = Contribution
        fields = ['type_contrib', 'contenu', 'fichier']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre contribution...'}),
        }


class CommentForm(forms.ModelForm):
    """
    Formulaire pour ajouter un nouveau commentaire à une contribution.
    """
    class Meta:
        model = Commentaire
        fields = ['contenu_com']
        widgets = {
            'contenu_com': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Votre commentaire...'}),
        }


class JoindreGroupeForm2(forms.ModelForm):
    # Champ pour choisir le groupe. Le queryset sera filtré dans la vue.
    groupe = forms.ModelChoiceField(
        queryset=GroupeDeTravail.objects.none(), # Initialement vide, sera rempli dynamiquement
        label="Sélectionnez un groupe",
        help_text="Choisissez un groupe de travail pour ce TP."
    )

    class Meta:
        model = EtudiantGroupe
        fields = ['groupe'] # Seul le champ 'groupe' est nécessaire dans ce formulaire

    def __init__(self, *args, **kwargs):
        self.travail = kwargs.pop('travail', None) # Récupère l'instance de Travail
        self.etudiant_instance = kwargs.pop('etudiant_instance', None) # Récupère l'instance de l'étudiant
        super().__init__(*args, **kwargs)

        if self.travail:
            # Filtre les groupes pour n'afficher que ceux liés à ce travail
            self.fields['groupe'].queryset = GroupeDeTravail.objects.filter(id_travail=self.travail)
        else:
            # Si aucun travail n'est passé, vide le queryset
            self.fields['groupe'].queryset = GroupeDeTravail.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        groupe = cleaned_data.get('groupe')

        # Vérifier si l'étudiant est déjà membre de ce groupe
        if self.etudiant_instance and groupe:
            if EtudiantGroupe.objects.filter(etudiant=self.etudiant_instance, groupe=groupe).exists():
                raise forms.ValidationError("Vous êtes déjà membre de ce groupe.")
        return cleaned_data

    def save(self, commit=True):
        etudiant_groupe = super().save(commit=False)
        etudiant_groupe.etudiant = self.etudiant_instance # Assigne l'étudiant au groupe
        if commit:
            etudiant_groupe.save()
        return etudiant_groupe


class UserProfileForm(forms.ModelForm):
    """
    Formulaire pour la modification des informations éditables du modèle User.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # Champs que l'utilisateur peut modifier
        # Les champs comme 'is_active', 'is_staff', 'date_joined', 'password'
        # ne sont PAS inclus car ils sont gérés par le système ou non-éditables directement.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rend le champ email non éditable s'il est déjà défini
        # L'email est souvent la clé d'identification unique et sa modification doit être gérée avec prudence.
        if self.instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].help_text = "L'adresse e-mail ne peut pas être modifiée ici. Contactez l'administrateur si nécessaire."


class EtudiantProfileForm(forms.ModelForm):
    """
    Formulaire pour la modification des informations du modèle Etudiant.
    """
    class Meta:
        model = Etudiant
        # Les champs 'user' (OneToOneField) et 'matricule' (primary_key, auto-généré)
        # ne sont PAS inclus pour la modification directe par l'utilisateur.
        fields = ['id_promotion', 'id_faculte']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rend le champ matricule en lecture seule si vous voulez l'afficher mais pas le modifier
        # self.fields['matricule'].widget.attrs['readonly'] = True
        # self.fields['matricule'].required = False # Non requis pour la modification


class ProfesseurProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="Prénom") # max_length de AbstractUser
    last_name = forms.CharField(max_length=150, required=True, label="Nom") # max_length de AbstractUser
    email = forms.EmailField(required=True, label="Email")
    specialite = forms.CharField(max_length=100, required=False, label="Spécialité", help_text="Ex: Mathématiques, Informatique")
    profile_picture = forms.ImageField(required=False, label="Photo de profil")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance: # Si c'est une instance existante (modification)
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email
            if hasattr(self.instance, 'professeur_profile'):
                self.fields['specialite'].initial = self.instance.professeur_profile.specialite
            self.fields['profile_picture'].initial = self.instance.profile_picture

        # Ajouter des classes Tailwind à tous les champs (sauf FileInput)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
            user.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            user.save()
            professeur_profile, created = Professeur.objects.get_or_create(user=user)
            professeur_profile.specialite = self.cleaned_data['specialite']
            professeur_profile.save()
        return user

class TravailForm(forms.ModelForm):
    """
    Formulaire pour la création d'un nouveau travail par un professeur.
    """
    class Meta:
        model = Travail
        fields = ['titre_tp', 'description', 'date_limit', 'id_cours', 'id_promo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez le travail...'}),
            'date_limit': forms.DateTimeInput(attrs={'type': 'datetime-local'}), # Nécessite format YYYY-MM-DDTHH:MM
        }

    def __init__(self, *args, **kwargs):
        self.professeur = kwargs.pop('professeur', None)
        super().__init__(*args, **kwargs)
        # Limiter les choix de cours aux cours enseignés par le professeur
        if self.professeur:
            self.fields['id_cours'].queryset = self.professeur.cours_enseignes.all()
            # Limiter les choix de promotion aux promotions associées aux cours enseignés par le professeur
            # distinct() est important pour éviter les doublons de promotions si plusieurs cours sont liés à la même promotion
            promotions_ids = Cours.objects.filter(id_professeur=self.professeur).values_list('id_promotion', flat=True)  
            self.fields['id_promo'].queryset = Promotion.objects.filter(id__in=promotions_ids)

            
            #promotions_ids = self.professeur.cours_enseignes.values_list('id_promotion', flat=True).distinct()
            #self.fields['id_promotion'].queryset = Promotion.objects.filter(id__in=promotions_ids)
        
        # Ajouter des classes Tailwind
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
        self.fields['date_limit'].widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})


class GroupeCreationForm(forms.ModelForm):
    """
    Formulaire pour la création d'un nouveau groupe de travail par un professeur.
    """
    class Meta:
        model = GroupeDeTravail
        fields = ['nom_groupe', 'id_travail', 'capacite_max', 'statut_groupe']
        widgets = {
            'statut_groupe': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }

    def __init__(self, *args, **kwargs):
        self.professeur = kwargs.pop('professeur', None)
        super().__init__(*args, **kwargs)
        # Limiter les choix de travail aux travaux créés par ce professeur
        if self.professeur:
            travaux_crees_ids = Travail.objects.filter(auteur=self.professeur).values_list('id', flat=True)
            self.fields['id_travail'].queryset = Travail.objects.filter(id__in=travaux_crees_ids)
        
        # Ajouter des classes Tailwind
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})

class AddStudentToGroupForm(forms.Form):
    """
    Formulaire pour ajouter un étudiant à un groupe existant.
    """
    etudiant = forms.ModelChoiceField(
        queryset=Etudiant.objects.all(),
        label="Sélectionner un étudiant",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )

    def __init__(self, *args, **kwargs):
        self.groupe = kwargs.pop('groupe', None)
        super().__init__(*args, **kwargs)
        
        if self.groupe:
            # Exclure les étudiants déjà membres du groupe
            membres_ids = self.groupe.membres.values_list('etudiant__id', flat=True)
            # Ne proposer que les étudiants de la promotion concernée par le travail du groupe
            promo_du_travail = self.groupe.id_travail.id_promotion
            self.fields['etudiant'].queryset = Etudiant.objects.filter(
                id_promotion=promo_du_travail
            ).exclude(id__in=membres_ids)
        else:
            self.fields['etudiant'].queryset = Etudiant.objects.none() # Aucun étudiant si pas de groupe

    def clean_etudiant(self):
        etudiant = self.cleaned_data['etudiant']
        if self.groupe and self.groupe.get_members_count() >= self.groupe.capacite_max:
            raise forms.ValidationError("Ce groupe a atteint sa capacité maximale.")
        return etudiant