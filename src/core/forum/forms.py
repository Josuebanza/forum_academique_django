# main/forms.py
from django import forms
from .models import (
    SujetDiscussion,
    User,
    Faculte,
    Promotion,
    Etudiant,
    Travail,
    Rapport,
    Contribution,
    Commentaire,
)
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