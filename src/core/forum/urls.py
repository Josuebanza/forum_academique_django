from django.urls import path, include
from django.contrib.auth import views as auth_views

from forum import views
from forum.views import inscription


urlpatterns = [
    # URL pour l'application principale
    
    path('inscription/', inscription, name='inscription'),
    path('login/', auth_views.LoginView.as_view(template_name='forum/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # URL pour la page d'accueil
    path('etudiant/', views.etudiant_home, name='etudiant_home'),
    path('professeur/', views.prof_home, name='prof_home'),
    
    # Password reset views
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='forum/reset.html'
    ), name='password_reset'),
     
    path('reset-password/', 
         auth_views.PasswordResetView.as_view(template_name='forum/password_reset.html'), 
         name='password_reset'),

    path('reset-password/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='forum/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='forum/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='forum/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # URL pour le tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    path('etudiant/',  views.etudiant_home, name='etudiant_home'),
    path('professeur/',views.prof_home,    name='prof_home'),
    

    # URL pour les fonctionnalités spécifiques
    path('prof/creer-travail/', views.creer_travail, name='creer_travail'),
    path('etudiant/nouveau-sujet/', views.nouveau_sujet, name='nouveau_sujet'),
    path('etudiant/groupe/<int:groupe_id>/rapport/', views.soumettre_rapport, name='soumettre_rapport'),


    path('travail/<int:tp_id>/', views.travail_detail, name='travail_detail'),
    path('sujet/<int:s_id>/',     views.sujet_detail,   name='sujet_detail'),
    
    
    path('react/<int:contrib_id>/', views.react, name='react'),
]
