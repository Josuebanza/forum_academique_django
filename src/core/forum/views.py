from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.urls import reverse

from forum.forms import (
    CommentForm, CustomUserCreationForm, RapportForm, SujetDiscussionForm,
    TravailForm, ContributionForm, CommentaireForm, UserProfileForm,
    EtudiantProfileForm, JoindreGroupeForm, ProfesseurProfileForm,
    GroupeCreationForm, AddStudentToGroupForm
)
from forum.models import (
    Commentaire, EtudiantGroupe, Reaction, Travail, GroupeDeTravail, Rapport,
    SujetDiscussion, Contribution, Etudiant, Professeur, Cours, Promotion, Faculte, User
)

# --- Utility ---

def is_professeur(user):
    return user.is_authenticated and getattr(user, 'user_type', None) == 'professeur'

# --- Auth & Dashboard ---

def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'forum/inscription.html', {'form': form})

@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile_type', None)
    if profile == 'etudiant':
        return redirect('etudiant_dashboard')
    elif profile == 'professeur':
        return redirect('prof_dashboard')
    elif request.user.is_superuser or profile == 'admin':
        return redirect('admin:index')
    return render(request, 'forum/dashboard.html')

# --- Etudiant Views ---

@login_required
def etudiant_home(request):
    if not getattr(request.user, 'is_etudiant', lambda: False)():
        return redirect('dashboard')
    try:
        etu = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas encore configuré. Veuillez contacter l'administrateur.")
        return redirect('inscription')
    travaux_affectes = Travail.objects.filter(id_promo=etu.id_promotion).order_by('-date_limit')
    mes_contributions = Contribution.objects.filter(auteur=etu).order_by('-date_post')
    context = {
        'etudiant': etu,
        'travaux': travaux_affectes,
        'contribs': mes_contributions,
    }
    return render(request, 'forum/etudiant_home.html', context)

@login_required
def etudiant_home2(request):
    promo = getattr(request.user, 'promotion', None)
    travaux = Travail.objects.filter(cours__promotion=promo)
    sujets = SujetDiscussion.objects.filter(promotion=promo)
    return render(request, 'forum/etudiant_home.html', {
        'travaux': travaux,
        'sujets': sujets,
    })

@login_required
def etudiant_home3(request):
    promo = request.user.etudiant_profile.id_promotion
    q = request.GET.get('q', '').strip()
    travaux_qs = Travail.objects.filter(id_promo__id_promotion=promo)
    if q:
        travaux_qs = travaux_qs.filter(
            Q(titre_tp__icontains=q) | Q(cours__titre__icontains=q)
        )
    travaux_paginator = Paginator(travaux_qs.order_by('-date_limit'), 5)
    page_travails = request.GET.get('page_tp')
    travaux = travaux_paginator.get_page(page_travails)
    return render(request, 'forum/etudiant_home.html', {
        'travaux': travaux,
        'q': q,
    })

# --- Professeur Views ---

@login_required
def prof_home(request):
    prof = request.user
    q = request.GET.get('q', '').strip()
    travaux_qs = Travail.objects.filter(auteur=prof.id)
    groupes_qs = GroupeDeTravail.objects.filter(id_travail__auteur=prof.id)
    rapports_qs = Rapport.objects.filter(id_groupe__in=groupes_qs)
    if q:
        travaux_qs = travaux_qs.filter(titre_tp__icontains=q)
        groupes_qs = groupes_qs.filter(nom_groupe__icontains=q)
        rapports_qs = rapports_qs.filter(groupe__nom_groupe__icontains=q)
    tp_pag = Paginator(travaux_qs.order_by('-date_limit'), 5)
    gr_pag = Paginator(groupes_qs.order_by('nom_groupe'), 5)
    rp_pag = Paginator(rapports_qs.order_by('-date_soumission'), 5)
    travaux = tp_pag.get_page(request.GET.get('page_tp'))
    groupes = gr_pag.get_page(request.GET.get('page_grp'))
    rapports = rp_pag.get_page(request.GET.get('page_rp'))
    return render(request, 'forum/prof_home.html', {
        'travaux': travaux,
        'groupes': groupes,
        'rapports': rapports,
        'q': q,
    })

@login_required
def prof_home2(request):
    prof = request.user
    travaux = Travail.objects.filter(cours__professeur=prof)
    groupes = GroupeDeTravail.objects.filter(travail__in=travaux)
    rapports = Rapport.objects.filter(groupe__in=groupes)
    return render(request, 'forum/prof_home.html', {
        'travaux': travaux,
        'groupes': groupes,
        'rapports': rapports,
    })

# --- Travail, Sujet, Rapport ---

@login_required
def creer_travail(request):
    if getattr(request.user, 'profile_type', None) != 'professeur':
        return redirect('dashboard')
    if request.method == 'POST':
        form = TravailForm(request.POST)
        if form.is_valid():
            tp = form.save()
            messages.success(request, f"Travail « {tp.titre_tp} » créé !")
            return redirect('prof_home')
    else:
        form = TravailForm()
    return render(request, 'forum/creer_travail.html', {'form': form})

@login_required
def nouveau_sujet(request):
    if getattr(request.user, 'profile_type', None) != 'etudiant':
        return redirect('dashboard')
    if request.method == 'POST':
        form = SujetDiscussionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sujet de discussion créé !")
            return redirect('etudiant_home')
    else:
        form = SujetDiscussionForm()
    return render(request, 'forum/nouveau_sujet.html', {'form': form})

@login_required
def soumettre_rapport(request, groupe_id):
    groupe = get_object_or_404(GroupeDeTravail, id=groupe_id)
    if getattr(request.user, 'profile_type', None) != 'etudiant' or request.user not in groupe.membres.all():
        return redirect('dashboard')
    if request.method == 'POST':
        form = RapportForm(request.POST, request.FILES)
        if form.is_valid():
            rap = form.save(commit=False)
            rap.groupe = groupe
            rap.save()
            messages.success(request, "Rapport soumis avec succès !")
            return redirect('etudiant_home')
    else:
        form = RapportForm()
    return render(request, 'forum/soumettre_rapport.html', {'form': form, 'groupe': groupe})

# --- Travail & Sujet Detail ---

@login_required
def travail_detail(request, tp_id):
    tp = get_object_or_404(Travail, id=tp_id)
    contribs = Contribution.objects.filter(travail=tp).annotate(
        likes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.J_AIME)),
        dislikes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.JE_DETESTE))
    )
    c_form = ContributionForm(prefix='c')
    cm_form = CommentaireForm(prefix='cm')
    if request.method == 'POST':
        if 'c-submit' in request.POST:
            c_form = ContributionForm(request.POST, request.FILES, prefix='c')
            if c_form.is_valid():
                nc = c_form.save(commit=False)
                nc.etudiant = request.user
                nc.travail = tp
                nc.save()
                return redirect('travail_detail', tp_id=tp.id)
        elif 'cm-submit' in request.POST:
            cm_form = CommentaireForm(request.POST, prefix='cm')
            if cm_form.is_valid():
                cc = cm_form.save(commit=False)
                cc.etudiant = request.user
                contrib_pk = request.POST.get('contrib_id')
                cc.contribution = get_object_or_404(Contribution, pk=contrib_pk)
                cc.save()
                return redirect('travail_detail', tp_id=tp.id)
    return render(request, 'forum/travail_detail.html', {
        'tp': tp, 'contribs': contribs,
        'c_form': c_form, 'cm_form': cm_form,
    })

@login_required
def sujet_detail(request, s_id):
    sujet = get_object_or_404(SujetDiscussion, id=s_id)
    contribs = Contribution.objects.filter(sujet=sujet).annotate(
        likes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.J_AIME)),
        dislikes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.JE_DETESTE))
    )
    c_form = ContributionForm(prefix='c')
    cm_form = CommentaireForm(prefix='cm')
    if request.method == 'POST':
        if 'c-submit' in request.POST:
            c_form = ContributionForm(request.POST, request.FILES, prefix='c')
            if c_form.is_valid():
                nc = c_form.save(commit=False)
                nc.etudiant = request.user
                nc.sujet = sujet
                nc.save()
                return redirect('sujet_detail', s_id=sujet.id)
        elif 'cm-submit' in request.POST:
            cm_form = CommentaireForm(request.POST, prefix='cm')
            if cm_form.is_valid():
                cc = cm_form.save(commit=False)
                cc.etudiant = request.user
                contrib_pk = request.POST.get('contrib_id')
                cc.contribution = get_object_or_404(Contribution, pk=contrib_pk)
                cc.save()
                return redirect('sujet_detail', s_id=sujet.id)
    return render(request, 'forum/sujet_detail.html', {
        'sujet': sujet, 'contribs': contribs,
        'c_form': c_form, 'cm_form': cm_form,
    })

# --- Reaction ---

@login_required
def react(request, contrib_id):
    if request.method != 'POST':
        return redirect('dashboard')
    contrib = get_object_or_404(Contribution, id=contrib_id)
    user = request.user
    typ = request.POST.get('reaction')
    if typ not in dict(Reaction.TYPE_R):
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    reaction, created = Reaction.objects.get_or_create(
        utilisateur=user,
        contribution=contrib,
        defaults={'type_reaction': typ}
    )
    if not created:
        if reaction.type_reaction == typ:
            reaction.delete()
        else:
            reaction.type_reaction = typ
            reaction.save()
    if contrib.travail:
        return redirect('travail_detail', tp_id=contrib.travail.id)
    return redirect('sujet_detail', s_id=contrib.sujet.id)

# --- Forum Travail/Contribution/Commentaire ---

@login_required
def travail_forum_view(request, travail_id):
    travail = get_object_or_404(Travail, pk=travail_id)
    if not getattr(request.user, 'is_etudiant', lambda: False)():
        messages.warning(request, "Seuls les étudiants peuvent accéder au forum des travaux.")
        return redirect('dashboard')
    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas configuré. Veuillez contacter l'administrateur.")
        return redirect('dashboard')
    est_membre_groupe = EtudiantGroupe.objects.filter(
        etudiant=etudiant_profile,
        groupe__id_travail=travail
    ).exists()
    if not est_membre_groupe:
        messages.error(request, "Vous devez être membre d'un groupe pour ce travail pour accéder au forum.")
        return redirect('joindre_groupe', travail_id=travail_id)
    contribution_form = ContributionForm()
    if request.method == 'POST':
        contribution_form = ContributionForm(request.POST, request.FILES)
        if contribution_form.is_valid():
            new_contribution = contribution_form.save(commit=False)
            new_contribution.auteur = etudiant_profile
            new_contribution.id_travail = travail
            new_contribution.save()
            messages.success(request, "Votre contribution a été ajoutée avec succès !")
            return redirect('travail_forum_view', travail_id=travail.id)
        else:
            messages.error(request, "Erreur lors de l'ajout de votre contribution. Veuillez vérifier les champs.")
    contributions = Contribution.objects.filter(id_travail=travail).select_related('auteur__user').annotate(
        num_commentaires=Count('commentaires', distinct=True),
        num_likes=Count('reactions', filter=Q(reactions__type_reaction='like'), distinct=True),
        num_dislikes=Count('reactions', filter=Q(reactions__type_reaction='dislike'), distinct=True)
    ).order_by('-date_post')
    sort_by = request.GET.get('sort', 'date_post')
    if sort_by == 'likes':
        contributions = contributions.order_by('-num_likes', '-date_post')
    elif sort_by == 'dislikes':
        contributions = contributions.order_by('-num_dislikes', '-date_post')
    elif sort_by == 'comments':
        contributions = contributions.order_by('-num_commentaires', '-date_post')
    paginator = Paginator(contributions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'travail': travail,
        'page_obj': page_obj,
        'page_param': 'page',
        'contributions': page_obj.object_list,
        'contribution_form': contribution_form,
        'sort_by': sort_by,
        'etudiant': etudiant_profile,
    }
    return render(request, 'forum/travail_forum.html', context)

@login_required
def commentaire_detail_view(request, contribution_id):
    contribution = get_object_or_404(Contribution, pk=contribution_id)
    if not getattr(request.user, 'is_etudiant', lambda: False)():
        messages.warning(request, "Seuls les étudiants peuvent commenter les contributions.")
        return redirect('dashboard')
    try:
        etudiant_profile = request.user.etudiant_profile
    except Etudiant.DoesNotExist:
        messages.error(request, "Votre profil étudiant n'est pas configuré. Veuillez contacter l'administrateur.")
        return redirect('dashboard')
    est_membre_groupe = EtudiantGroupe.objects.filter(
        etudiant=etudiant_profile,
        groupe__id_travail=contribution.id_travail
    ).exists()
    if not est_membre_groupe:
        messages.error(request, "Vous devez être membre d'un groupe pour accéder aux commentaires de ce travail.")
        return redirect('joindre_groupe', travail_id=contribution.id_travail.id)
    comment_form = CommentForm()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.auteur = etudiant_profile
            new_comment.id_contribution = contribution
            new_comment.save()
            messages.success(request, "Votre commentaire a été ajouté avec succès !")
            return redirect('commentaire_detail_view', contribution_id=contribution.id)
        else:
            messages.error(request, "Erreur lors de l'ajout de votre commentaire. Veuillez vérifier le champ.")
    commentaires = Commentaire.objects.filter(id_contribution=contribution).select_related('auteur__user').order_by('date_com')
    user_reaction = Reaction.objects.filter(
        etudiant=etudiant_profile,
        contribution=contribution
    ).first()
    context = {
        'contribution': contribution,
        'commentaires': commentaires,
        'comment_form': comment_form,
        'user_reaction': user_reaction,
        'etudiant': etudiant_profile,
    }
    return render(request, 'forum/commentaire_detail.html', context)

@login_required
def react_to_contribution(request, contribution_id, reaction_type):
    if not getattr(request.user, 'is_etudiant', lambda: False)():
        messages.warning(request, "Vous devez être un étudiant pour réagir.")
        return redirect('dashboard')
    etudiant_profile = get_object_or_404(Etudiant, user=request.user)
    contribution = get_object_or_404(Contribution, pk=contribution_id)
    est_membre_groupe = EtudiantGroupe.objects.filter(
        etudiant=etudiant_profile,
        groupe__id_travail=contribution.id_travail
    ).exists()
    if not est_membre_groupe:
        messages.error(request, "Vous devez être membre d'un groupe pour réagir aux contributions de ce travail.")
        return redirect('joindre_groupe', travail_id=contribution.id_travail.id)
    existing_reaction = Reaction.objects.filter(
        etudiant=etudiant_profile,
        contribution=contribution
    ).first()
    if existing_reaction:
        if existing_reaction.type_reaction == reaction_type:
            existing_reaction.delete()
            messages.info(request, f"Votre {reaction_type} a été retiré.")
        else:
            existing_reaction.type_reaction = reaction_type
            existing_reaction.save()
            messages.success(request, f"Votre réaction a été changée en {reaction_type}.")
    else:
        Reaction.objects.create(
            etudiant=etudiant_profile,
            contribution=contribution,
            type_reaction=reaction_type
        )
        messages.success(request, f"Vous avez réagi avec un {reaction_type} !")
    return redirect('travail_forum_view', travail_id=contribution.id_travail.id)

# --- Professeur Dashboard & Management ---

@login_required
#@user_passes_test(is_professeur, login_url='prof_dashboard')
def prof_dashboard(request):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    cours_enseignes = professeur_profile.cours_enseignes.all()
    travaux_crees = Travail.objects.filter(auteur=professeur_profile).order_by('-date_post')
    groupes_geres = GroupeDeTravail.objects.filter(id_travail__auteur=professeur_profile).order_by(
        'id_travail__titre_tp', 'nom_groupe'
    )
    if request.method == 'POST':
        profile_form = ProfesseurProfileForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('prof_dashboard')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil. Veuillez vérifier les informations.")
    else:
        profile_form = ProfesseurProfileForm(instance=request.user)
    context = {
        'professeur': professeur_profile,
        'cours_enseignes': cours_enseignes,
        'travaux_crees': travaux_crees,
        'groupes_geres': groupes_geres,
        'profile_form': profile_form,
    }
    return render(request, 'forum/prof/prof_dashboard.html', context)

@login_required
#@user_passes_test(is_professeur, login_url='dashboard')
def prof_creer_travail(request):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    if request.method == 'POST':
        form = TravailForm(request.POST, professeur=professeur_profile)
        if form.is_valid():
            travail = form.save(commit=False)
            travail.auteur = professeur_profile
            travail.save()
            messages.success(request, "Le travail a été créé avec succès !")
            return redirect('prof_dashboard')
        else:
            messages.error(request, "Erreur lors de la création du travail. Veuillez vérifier les champs.")
            context = {'form': form, 'professeur': professeur_profile}
            return render(request, 'forum/prof/prof_creer_travail.html', context)
    else:
        form = TravailForm(professeur=professeur_profile)
    context = {
        'form': form,
        'professeur': professeur_profile,
    }
    return render(request, 'forum/prof/prof_creer_travail.html', context)

@login_required
@user_passes_test(is_professeur, login_url='dashboard')
def prof_voir_travail(request, travail_id):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    travail = get_object_or_404(Travail, pk=travail_id, auteur=professeur_profile)
    if request.method == 'POST':
        form = TravailForm(request.POST, instance=travail, professeur=professeur_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Le travail a été mis à jour avec succès !")
            return redirect('prof_voir_travail', travail_id=travail.id)
        else:
            messages.error(request, "Erreur lors de la modification du travail.")
            context = {'travail': travail, 'professeur': professeur_profile, 'form': form}
            return render(request, 'forum/prof/prof_voir_travail.html', context)
    else:
        form = TravailForm(instance=travail, professeur=professeur_profile)
    context = {
        'travail': travail,
        'professeur': professeur_profile,
        'form': form,
    }
    return render(request, 'forum/prof/prof_voir_travail.html', context)

@login_required
#@user_passes_test(is_professeur, login_url='dashboard')
def prof_creer_groupe(request):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    if request.method == 'POST':
        form = GroupeCreationForm(request.POST, professeur=professeur_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Le groupe a été créé avec succès !")
            return redirect('prof_dashboard')
        else:
            messages.error(request, "Erreur lors de la création du groupe. Veuillez vérifier les champs.")
            context = {'form': form, 'professeur': professeur_profile}
            return render(request, 'forum/prof/prof_creer_groupe.html', context)
    else:
        form = GroupeCreationForm(professeur=professeur_profile)
    context = {
        'form': form,
        'professeur': professeur_profile,
    }
    return render(request, 'forum/prof/prof_creer_groupe.html', context)

@login_required
#@user_passes_test(is_professeur, login_url='dashboard')
def prof_gerer_groupe(request, groupe_id):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    groupe = get_object_or_404(GroupeDeTravail, pk=groupe_id, id_travail__auteur=professeur_profile)
    membres_actuels = groupe.membres.select_related('etudiant__user', 'etudiant__id_promotion').all()
    add_student_form = AddStudentToGroupForm(groupe=groupe)
    if request.method == 'POST':
        if 'add_student' in request.POST:
            add_student_form = AddStudentToGroupForm(request.POST, groupe=groupe)
            if add_student_form.is_valid():
                etudiant_a_ajouter = add_student_form.cleaned_data['etudiant']
                try:
                    EtudiantGroupe.objects.create(etudiant=etudiant_a_ajouter, groupe=groupe)
                    messages.success(request, f"{etudiant_a_ajouter.user.first_name} {etudiant_a_ajouter.user.last_name} a été ajouté au groupe.")
                    return redirect('prof_gerer_groupe', groupe_id=groupe.id)
                except Exception as e:
                    messages.error(request, f"Impossible d'ajouter l'étudiant : {e}. Il est peut-être déjà membre ou le groupe est plein.")
            else:
                messages.error(request, "Erreur lors de l'ajout de l'étudiant. Veuillez vérifier les champs.")
                context = {
                    'professeur': professeur_profile,
                    'groupe': groupe,
                    'membres_actuels': membres_actuels,
                    'add_student_form': add_student_form,
                }
                return render(request, 'forum/prof/prof_gerer_groupe.html', context)
        elif 'remove_student' in request.POST:
            etudiant_id_a_retirer = request.POST.get('etudiant_id_to_remove')
            etudiant_groupe_instance = get_object_or_404(EtudiantGroupe, etudiant__id=etudiant_id_a_retirer, groupe=groupe)
            etudiant_groupe_instance.delete()
            messages.success(request, "L'étudiant a été retiré du groupe.")
            return redirect('prof_gerer_groupe', groupe_id=groupe.id)
    context = {
        'professeur': professeur_profile,
        'groupe': groupe,
        'membres_actuels': membres_actuels,
        'add_student_form': add_student_form,
    }
    return render(request, 'forum/prof/prof_gerer_groupe.html', context)

@login_required
#@user_passes_test(is_professeur, login_url='dashboard')
def prof_liste_etudiants(request):
    professeur_profile = get_object_or_404(Professeur, user=request.user)
    facultes = Faculte.objects.all()
    promotions = Promotion.objects.all()
    cours_enseignes_filter = professeur_profile.cours_enseignes.all()
    etudiants_queryset = Etudiant.objects.select_related('user', 'id_faculte', 'id_promotion').all().order_by(
        'id_faculte', 'id_promotion', 'user__last_name'
    )
    filter_fac = request.GET.get('faculte')
    filter_promo = request.GET.get('promotion')
    filter_cours = request.GET.get('cours')
    if filter_fac:
        etudiants_queryset = etudiants_queryset.filter(id_faculte__id=filter_fac)
    if filter_promo:
        etudiants_queryset = etudiants_queryset.filter(id_promotion__id=filter_promo)
    if filter_cours:
        cours_obj = get_object_or_404(Cours, id=filter_cours)
        etudiants_queryset = etudiants_queryset.filter(id_promotion=cours_obj.id_promotion)
    paginator = Paginator(etudiants_queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'professeur': professeur_profile,
        'page_obj': page_obj,
        'etudiants': page_obj.object_list,
        'facultes': facultes,
        'promotions': promotions,
        'cours_enseignes_filter': cours_enseignes_filter,
        'selected_fac': filter_fac,
        'selected_promo': filter_promo,
        'selected_cours': filter_cours,
    }
    return render(request, 'forum/prof/prof_liste_etudiants.html', context)
