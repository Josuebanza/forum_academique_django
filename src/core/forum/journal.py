# forum/views.py
# 🌸 Importations magiques pour un journal étudiant tout doux ! 🌸
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Pour les messages de feedback tout mignons
from .models import Etudiant, Travail, GroupeDeTravail, EtudiantGroupe  # Nos modèles adorés
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import EtudiantProfileForm, JoindreGroupeForm, UserProfileForm  # Les formulaires qui facilitent la vie


# ... (vos autres vues existantes comme etudiant_home, prof_home, etc.) ...

def etudiant_home4(request):
    # Get the student's group(s) - assuming students belong to groups
    # This is an example; adjust based on how you link students to groups/travaux
    try:
        student_group = request.user.groupe # Assuming a ForeignKey from User to Groupe
    except AttributeError:
        # Handle cases where user might not be linked to a group yet
        student_group = None

    travaux = []
    if student_group:
        # Filter travaux relevant to the student's group
        travaux = Travail.objects.filter(groupe=student_group).order_by('-date_creation')
    else:
        # Handle cases where no group is associated, maybe show all or none
        # For now, let's assume no travaux if no group
        pass

    paginator = Paginator(travaux, 10) # Show 10 travaux per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'page_param': 'page', # Pass the parameter name for pagination
        # You might also want to pass the raw travaux list if not paginating immediately
    }
    return render(request, 'forum/etudiant_home.html', context)

# ... travail_detail view ...
def travail_detail(request, tp_id):
    travail = get_object_or_404(Travail, pk=tp_id)
    context = {
        'travail': travail
    }
    return render(request, 'forum/travail_detail.html', context)



def journal_travaux_etudiant(request):
    """
    Affiche le fil de contenu (journal) des travaux pour l'étudiant connecté,
    filtré par sa promotion.
    """
    
    if not request.user.is_etudiant():
        messages.warning(request, "Seuls les étudiants peuvent accéder à cette page.")
        return redirect('dashboard') # Redirige vers le tableau de bord général ou autre

    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas encore configuré. Veuillez contacter l'administrateur.")
        return redirect('dashboard')

    if not etudiant_profile.id_promotion:
        messages.info(request, "Votre promotion n'est pas définie. Aucun travail ne peut être affiché.")
        travaux_list = Travail.objects.none() # Aucune travail si pas de promotion
    else:
        # Filtre les travaux par la promotion de l'étudiant
        travaux_list = Travail.objects.filter(id_promo=etudiant_profile.id_promotion).order_by('-date_limit')

    # Pagination
    paginator = Paginator(travaux_list, 5) # 5 travaux par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'etudiant': etudiant_profile,
        'page_obj': page_obj,
        'page_param': 'page', # Nom du paramètre de la page pour la pagination
        'travaux_affectes': page_obj.object_list # Les objets de la page actuelle
    }
    return render(request, 'forum/travail_journal.html', context)


@login_required
def joindre_groupe(request, travail_id):
    """
    Affiche les détails d'un travail et permet à l'étudiant de rejoindre un groupe.
    """
    if not request.user.is_etudiant():
        messages.warning(request, "Seuls les étudiants peuvent rejoindre un groupe.")
        return redirect('dashboard')

    travail = get_object_or_404(Travail, pk=travail_id)
    
    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas configuré. Veuillez contacter l'administrateur.")
        return redirect('dashboard')

    # Récupérer les groupes existants pour ce travail
    groupes_disponibles = GroupeDeTravail.objects.filter(id_travail=travail)
    
    # Vérifier si l'étudiant est déjà dans un groupe pour ce travail
    etudiant_est_membre = EtudiantGroupe.objects.filter(
        etudiant=etudiant_profile,
        groupe__id_travail=travail # Vérifie si le groupe est lié à ce travail
    ).exists()

    form = JoindreGroupeForm(travail=travail, etudiant_instance=etudiant_profile)

    if request.method == 'POST':
        form = JoindreGroupeForm(request.POST, travail=travail, etudiant_instance=etudiant_profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"Vous avez rejoint le groupe '{form.cleaned_data['groupe'].nom_groupe}' avec succès !")
                return redirect('journal_travaux_etudiant') # Redirige vers le journal après succès
            except Exception as e:
                messages.error(request, f"Erreur lors de l'adhésion au groupe: {e}")
        else:
            # Les erreurs de validation du formulaire seront affichées automatiquement
            # dans le template si vous utilisez {{ form.as_p }} ou similar
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur pour {field}: {error}")

    context = {
        'travail': travail,
        'groupes_disponibles': groupes_disponibles,
        'form': form,
        'etudiant_est_membre': etudiant_est_membre, # Passe cette variable au template
        'etudiant': etudiant_profile,
    }
    return render(request, 'forum/joindre_groupe.html', context)


@login_required
def etudiant_dashboard(request):
    """
    Vue principale du tableau de bord étudiant, affichant les travaux filtrés,
    les groupes de l'étudiant et le formulaire de profil.
    """
    # 1. Vérification du profil étudiant
    if not request.user.is_etudiant():
        messages.warning(request, "Seuls les étudiants peuvent accéder à cette page.")
        return redirect('dashboard') # Redirige vers le tableau de bord général

    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas encore configuré. Veuillez contacter l'administrateur.")
        # Optionnel: Tu peux rediriger vers une page de setup du profil si tu en as une
        return redirect('dashboard')

    # 2. Gestion de la modification de profil (POST request)
    user_form = UserProfileForm(instance=request.user)
    etudiant_form = EtudiantProfileForm(instance=etudiant_profile)

    if request.method == 'POST':
        # Déterminez quel formulaire a été soumis
        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            etudiant_form = EtudiantProfileForm(request.POST, instance=etudiant_profile)

            if user_form.is_valid() and etudiant_form.is_valid():
                user_form.save()
                etudiant_form.save()
                messages.success(request, "Vos informations de profil ont été mises à jour avec succès !")
                return redirect('etudiant_dashboard') # Redirige pour éviter la soumission multiple
            else:
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire de profil.")
        # Ajoutez ici la logique pour d'autres formulaires POST si vous en avez sur la même page
 
    # 3. Récupération des travaux filtrés et recherche
    travaux_list = Travail.objects.none() # Par défaut, aucun travail
    search_query = request.GET.get('q', '') # Récupère le terme de recherche
    
    if etudiant_profile.id_promotion:
        travaux_queryset = Travail.objects.filter(id_promo=etudiant_profile.id_promotion)

        if search_query:
            # Recherche par titre du TP ou titre du cours
            travaux_queryset = travaux_queryset.filter(
                Q(titre_tp__icontains=search_query) |
                Q(id_cours__titre_cours__icontains=search_query)
            )
        travaux_list = travaux_queryset.order_by('-date_limit')
    else:
        messages.info(request, "Votre promotion n'est pas définie. Aucun travail ne peut être affiché.")

    # Pagination des travaux
    paginator = Paginator(travaux_list, 5) # 5 travaux par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 4. Récupération des groupes de l'étudiant
    # Cela suppose que EtudiantGroupe est bien rempli pour l'étudiant
    mes_groupes = EtudiantGroupe.objects.filter(etudiant=etudiant_profile).select_related('groupe__id_travail')

    context = {
        'etudiant': etudiant_profile,
        'user_form': user_form,
        'etudiant_form': etudiant_form,
        'search_query': search_query,
        'page_obj': page_obj, # Objet paginé des travaux
        'page_param': 'page', # Paramètre pour la pagination
        'travaux_affectes': page_obj.object_list, # Les objets réels pour l'itération
        'mes_groupes': mes_groupes,
    }
    return render(request, 'forum/etudiant_dashboard.html', context)

# ... (gardez vos autres vues comme joindre_groupe, travail_detail, etc.) ...



@login_required
def journal_travaux_etudiant(request):
    """
    Affiche le fil de contenu (journal) des travaux pour l'étudiant connecté,
    filtré par sa promotion.
    """
    if not request.user.is_etudiant():
        messages.warning(request, "Seuls les étudiants peuvent accéder à cette page.")
        return redirect('dashboard') # Redirige vers le tableau de bord général ou autre

    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas encore configuré. Veuillez contacter l'administrateur.")
        return redirect('dashboard')

    if not etudiant_profile.id_promotion:
        messages.info(request, "Votre promotion n'est pas définie. Aucun travail ne peut être affiché.")
        travaux_list = Travail.objects.none() # Aucune travail si pas de promotion
    else:
        # Filtre les travaux par la promotion de l'étudiant
        travaux_list = Travail.objects.filter(id_promo=etudiant_profile.id_promotion).order_by('-date_limit')

    # Pagination
    paginator = Paginator(travaux_list, 5) # 5 travaux par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'etudiant': etudiant_profile,
        'page_obj': page_obj,
        'page_param': 'page', # Nom du paramètre de la page pour la pagination
        'travaux_affectes': page_obj.object_list # Les objets de la page actuelle
    }
    return render(request, 'forum/travail_journal.html', context)
