from django.urls import path
from django.contrib.auth import views as auth_views

from forum import api as api
from forum import journal as journal
from forum.journal import journal_travaux_etudiant, joindre_groupe, etudiant_dashboard
from forum import views
from forum.views import inscription


urlpatterns = [
     # Auth & Registration
     path('inscription/', inscription, name='inscription'),
     path('login/', auth_views.LoginView.as_view(template_name='forum/login.html'), name='login'),
     path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

     # Password reset views
     path('reset-password/', auth_views.PasswordResetView.as_view(template_name='forum/password_reset.html'), name='password_reset'),
     path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='forum/password_reset_done.html'), name='password_reset_done'),
     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='forum/password_reset_confirm.html'), name='password_reset_confirm'),
     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='forum/password_reset_complete.html'), name='password_reset_complete'),

     # Home & Dashboard
     path('dashboard/', views.dashboard, name='dashboard'),
     path('etudiant/', views.etudiant_home, name='etudiant_home'),
     path('professeur/', views.prof_home, name='prof_home'),
     path('etudiant/dashboard/', journal.etudiant_dashboard, name='etudiant_dashboard'),


     # Professeur URLs
     path('prof/creer-travail/', views.creer_travail, name='creer_travail'),

     # Etudiant URLs
     path('etudiant/nouveau-sujet/', views.nouveau_sujet, name='nouveau_sujet'),
     path('etudiant/groupe/<int:groupe_id>/rapport/', views.soumettre_rapport, name='soumettre_rapport'),

     # Travail & Sujet Details
     path('travail/<int:tp_id>/', views.travail_detail, name='travail_detail'),
     path('sujet/<int:s_id>/', views.sujet_detail, name='sujet_detail'),

     # Forum & Contributions
     path('travail/<int:travail_id>/forum/', views.travail_forum_view, name='travail_forum_view'),
     path('contribution/<int:contribution_id>/commentaires/', views.commentaire_detail_view, name='commentaire_detail_view'),
     path('contribution/<int:contribution_id>/react/<str:reaction_type>/', views.react_to_contribution, name='react_to_contribution'),
     path('react/<int:contrib_id>/', views.react, name='react'),

     # Journal & Group Join
     path('etudiant/journal/', journal.journal_travaux_etudiant, name='journal_travaux_etudiant'),
     path('etudiant/travail/<int:travail_id>/joindre-groupe/', journal.joindre_groupe, name='joindre_groupe'),

     # (Optional) If you want to use the views version instead of journal
     # path('etudiant/travail/<int:travail_id>/joindre-groupe/', views.joindre_groupe, name='joindre_groupe'),
     
     # URLs pour les professeurs
     path('prof/dashboard/', views.prof_dashboard, name='prof_dashboard'),
     path('prof/travail/creer/', views.prof_creer_travail, name='prof_creer_travail'),
     path('prof/travail/<int:travail_id>/', views.prof_voir_travail, name='prof_voir_travail'),
     path('prof/groupe/creer/', views.prof_creer_groupe, name='prof_creer_groupe'),
     path('prof/groupe/<int:groupe_id>/gerer/', views.prof_gerer_groupe, name='prof_gerer_groupe'),
     path('prof/etudiants/', views.prof_liste_etudiants, name='prof_liste_etudiants'),
     
     # URLs pour les étudiants

     # URLs de forum/commentaires/réactions (accessibles par profs et étudiants)
     path('travail/<int:travail_id>/forum/', views.travail_forum_view, name='travail_forum_view'),
     path('contribution/<int:contribution_id>/commentaires/', views.commentaire_detail_view, name='commentaire_detail_view'),
     path('contribution/<int:contribution_id>/react/<str:reaction_type>/', views.react_to_contribution, name='react_to_contribution'),

     # URL pour rejoindre un groupe (étudiants)
     path('etudiant/travail/<int:travail_id>/joindre-groupe/', journal.joindre_groupe, name='joindre_groupe'),
     
     # URLs pour le journal des travaux (étudiants)
     path('api/updates/<int:travail_id>/', api.api_updates, name='api_updates'),

]    

