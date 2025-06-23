from django.shortcuts import render, redirect
from forum.forms import CustomUserCreationForm, RapportForm, SujetDiscussionForm, TravailForm, ContributionForm, CommentaireForm
from django.db.models import Count

from django.contrib.auth.decorators import login_required
from forum.models import Reaction, Travail, GroupeDeTravail, Rapport, SujetDiscussion, Contribution

from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib import messages
from django.shortcuts import get_object_or_404


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirection après inscription
    else:
        form = CustomUserCreationForm()
    return render(request, 'forum/inscription.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user

    if user.profile_type == 'etudiant':
        return redirect('etudiant_home')  # à créer
    elif user.profile_type == 'professeur':
        return redirect('prof_home')  # à créer
    elif user.is_superuser or user.profile_type == 'admin':
        return redirect('admin:index')  # vers l'admin Django
    else:
        return render(request, 'forum/dashboard.html')  # fallback

@login_required
def etudiant_home(request):
    return render(request, 'forum/etudiant_home.html')

@login_required
def prof_home(request):
    return render(request, 'forum/prof_home.html')



@login_required
def dashboard(request):
    # redirection selon le type de profil
    profile = request.user.profile_type
    if profile == 'etudiant':
        return redirect('etudiant_home')
    elif profile == 'professeur':
        return redirect('prof_home')
    elif request.user.is_superuser or profile == 'admin':
        return redirect('admin:index')
    else:
        return render(request, 'forum/dashboard.html')  # page générique fallback



@login_required
def etudiant_home(request):
    promo = request.user.promotion

    # Recherche
    q = request.GET.get('q', '').strip()
    travaux_qs = Travail.objects.filter(cours__promotion=promo)
    #sujets_qs  = SujetDiscussion.objects.filter(promotion=promo)

    if q:
        travaux_qs = travaux_qs.filter(
            Q(titre_tp__icontains=q) |
            Q(cours__titre__icontains=q)
        )
        sujets_qs = sujets_qs.filter(
            Q(titre__icontains=q) |
            Q(description__icontains=q)
        )

    # Pagination
    travaux_paginator = Paginator(travaux_qs.order_by('-date_limit'), 5)  # 5/tranche
    sujets_paginator  = Paginator(sujets_qs.order_by('-id'),  5)

    page_travails = request.GET.get('page_tp')
    page_sujets   = request.GET.get('page_sujet')

    travaux = travaux_paginator.get_page(page_travails)
    sujets  = sujets_paginator.get_page(page_sujets)

    return render(request, 'forum/etudiant_home.html', {
        'travaux': travaux,
        'sujets':  sujets,
        'q':       q,
    })


@login_required
def prof_home(request):
    prof = request.user

    # Recherche
    q = request.GET.get('q', '').strip()
    travaux_qs = Travail.objects.filter(cours__professeur=prof)
    groupes_qs = GroupeDeTravail.objects.filter(travail__in=travaux_qs)
    rapports_qs= Rapport.objects.filter(groupe__in=groupes_qs)

    if q:
        travaux_qs = travaux_qs.filter(titre_tp__icontains=q)
        groupes_qs = groupes_qs.filter(nom_groupe__icontains=q)
        rapports_qs= rapports_qs.filter(groupe__nom_groupe__icontains=q)

    # Pagination
    tp_pag = Paginator(travaux_qs.order_by('-date_limit'), 5)
    gr_pag = Paginator(groupes_qs.order_by('nom_groupe'), 5)
    rp_pag = Paginator(rapports_qs.order_by('-date_soumission'), 5)

    travaux = tp_pag.get_page(request.GET.get('page_tp'))
    groupes = gr_pag.get_page(request.GET.get('page_grp'))
    rapports= rp_pag.get_page(request.GET.get('page_rp'))

    return render(request, 'forum/prof_home.html', {
        'travaux':  travaux,
        'groupes':  groupes,
        'rapports': rapports,
        'q':        q,
    })


@login_required
def etudiant_home2(request):
    # récupère tous les travaux et sujets pertinents pour sa promotion
    promo = request.user.promotion
    travaux = Travail.objects.filter(cours__promotion=promo)
    sujets = SujetDiscussion.objects.filter(promotion=promo)
    return render(request, 'forum/etudiant_home.html', {
        'travaux': travaux,
        'sujets': sujets,
    })

@login_required
def prof_home2(request):
    # récupère tous les travaux à corriger, les groupes et rapports
    prof = request.user
    travaux = Travail.objects.filter(cours__professeur=prof)
    groupes   = GroupeDeTravail.objects.filter(travail__in=travaux)
    rapports  = Rapport.objects.filter(groupe__in=groupes)
    return render(request, 'forum/prof_home.html', {
        'travaux': travaux,
        'groupes': groupes,
        'rapports': rapports,
    })
    


## Fonction pour créer un travail (TP)
@login_required
def creer_travail(request):
    if request.user.profile_type != 'professeur':
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

## Fonction pour créer un sujet de discussion
@login_required
def nouveau_sujet(request):
    if request.user.profile_type != 'etudiant':
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


## Fonction pour soumettre un rapport de groupe
@login_required
def soumettre_rapport(request, groupe_id):
    groupe = get_object_or_404(GroupeDeTravail, id=groupe_id)
    if request.user.profile_type != 'etudiant' or request.user not in groupe.membres.all():
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
    return render(request, 'forum/soumettre_rapport.html', {
        'form': form, 'groupe': groupe
    })



@login_required
def travail_detail(request, tp_id):
    tp = get_object_or_404(Travail, id=tp_id)
    # contributions liées
    contribs = Contribution.objects.filter(travail=tp).annotate(
        likes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.J_AIME)),
        dislikes=Count('reaction', filter=Q(reaction__type_reaction=Reaction.JE_DETESTE))
    )
    # forms init
    c_form = ContributionForm(prefix='c')
    cm_form= CommentaireForm(prefix='cm')
    if request.method=='POST':
        if 'c-submit' in request.POST:
            c_form = ContributionForm(request.POST, request.FILES, prefix='c')
            if c_form.is_valid():
                nc = c_form.save(commit=False)
                nc.etudiant  = request.user
                nc.travail = tp
                nc.save()
                return redirect('travail_detail', tp_id=tp.id)
        elif 'cm-submit' in request.POST:
            cm_form = CommentaireForm(request.POST, prefix='cm')
            if cm_form.is_valid():
                cc = cm_form.save(commit=False)
                cc.etudiant       = request.user
                # need a contrib id in POST
                contrib_pk = request.POST.get('contrib_id')
                cc.contribution = get_object_or_404(Contribution, pk=contrib_pk)
                cc.save()
                return redirect('travail_detail', tp_id=tp.id)

    return render(request, 'forum/travail_detail.html',{
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
    cm_form= CommentaireForm(prefix='cm')
    if request.method=='POST':
        if 'c-submit' in request.POST:
            c_form = ContributionForm(request.POST, request.FILES, prefix='c')
            if c_form.is_valid():
                nc = c_form.save(commit=False)
                nc.etudiant = request.user
                nc.sujet  = sujet
                nc.save()
                return redirect('sujet_detail', s_id=sujet.id)
        elif 'cm-submit' in request.POST:
            cm_form = CommentaireForm(request.POST, prefix='cm')
            if cm_form.is_valid():
                cc = cm_form.save(commit=False)
                cc.etudiant       = request.user
                contrib_pk = request.POST.get('contrib_id')
                cc.contribution = get_object_or_404(Contribution, pk=contrib_pk)
                cc.save()
                return redirect('sujet_detail', s_id=sujet.id)

    return render(request, 'forum/sujet_detail.html',{
        'sujet': sujet, 'contribs': contribs,
        'c_form': c_form, 'cm_form': cm_form,
    })


@login_required
def react(request, contrib_id):
    if request.method != 'POST':
        return redirect('dashboard')

    contrib = get_object_or_404(Contribution, id=contrib_id)
    user    = request.user
    typ     = request.POST.get('reaction')  # 'LIKE' ou 'DISLIKE'

    # Vérifie que c'est un type valide
    if typ not in dict(Reaction.TYPE_R):
        return redirect(request.META.get('HTTP_REFERER','dashboard'))

    # Récupère une éventuelle réaction existante
    reaction, created = Reaction.objects.get_or_create(
        utilisateur=user,
        contribution=contrib,
        defaults={'type_reaction': typ}
    )

    if not created:
        if reaction.type_reaction == typ:
            # même réaction : on supprime (toggle off)
            reaction.delete()
        else:
            # type différent : on met à jour
            reaction.type_reaction = typ
            reaction.save()

    # redirige vers la page de détail appropriée
    if contrib.travail:
        return redirect('travail_detail', tp_id=contrib.travail.id)
    else:
        return redirect('sujet_detail', s_id=contrib.sujet.id)