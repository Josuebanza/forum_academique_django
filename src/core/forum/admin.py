# main/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Commentaire, Contribution, Cours, Etudiant, EtudiantGroupe, Faculte, GroupeDeTravail, Professeur, Promotion, Rapport, Reaction, Travail, User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profil', {'fields': ('profile_type',)}),
        ('Infos personnelles', {'fields': ('first_name','last_name',)}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        #('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','profile_type','password1','password2', 'first_name', 'last_name',),
        }),
    )
    list_display = ('email','profile_type','is_staff','last_login','date_joined')
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(Faculte)
admin.site.register(Promotion)
admin.site.register(Professeur)
admin.site.register(Cours)
admin.site.register(Travail)
admin.site.register(GroupeDeTravail)
admin.site.register(Rapport)
admin.site.register(Contribution)
admin.site.register(Commentaire)
admin.site.register(Reaction)
admin.site.register(EtudiantGroupe)
admin.site.register(Etudiant)

#admin.site.register(GroupeDebat)
#admin.site.register(ParticipeA)
#admin.site.register(Domaine)

# Configuration de l'interface d'administration
admin.site.site_header = "Administration du Forum UCC"
admin.site.site_title = "Forum UCC Admin"
admin.site.index_title = "Bienvenue dans l'administration du Forum UCC"
admin.site.empty_value_display = 'Non renseigné'
admin.site.site_url = None  # Désactive le lien vers le site principal

