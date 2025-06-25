# forum/views.py
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import Contribution, Commentaire, Reaction

@require_GET
def api_updates(request, travail_id):
    """
    Renvoie les contributions, commentaires et réactions créés
    depuis le timestamp "since" (GET ?since=ISO_TIMESTAMP).
    """
    # 1. Récupérer le paramètre since (ISO format)
    since = request.GET.get('since')
    try:
        since_dt = timezone.datetime.fromisoformat(since)
    except Exception:
        # Si absent ou invalide, on prend les 5 dernières secondes
        since_dt = timezone.now() - timezone.timedelta(seconds=5)

    # 2. Filtrer chaque modèle sur date_post > since
    contribs = Contribution.objects.filter(
        id_travail_id=travail_id,
        date_post__gt=since_dt
    ).select_related('auteur__user').order_by('date_post')

    comments = Commentaire.objects.filter(
        id_contribution__id_travail_id=travail_id,
        date_com__gt=since_dt
    ).select_related('auteur__user').order_by('date_com')

    # Pour Reaction, on n’a pas de date : on renvoie toujours toutes
    reacts = Reaction.objects.filter(
        contribution__id_travail_id=travail_id
    ).order_by('id')

    # 3. Construire la réponse JSON
    data = {
        'now': timezone.now().isoformat(),
        'contributions': [
            {
                'id': c.id,
                'auteur': c.auteur.user.first_name,
                'texte': c.contenu or '',
                'fichier_url': c.fichier.url if c.fichier else None,
                'date_post': c.date_post.isoformat(),
            } for c in contribs
        ],
        'commentaires': [
            {
                'id': cm.id,
                'auteur': cm.auteur.user.first_name,
                'contenu': cm.contenu_com,
                'date_com': cm.date_com.isoformat(),
                'contrib_id': cm.id_contribution_id,
            } for cm in comments
        ],
        'reactions': [
            {
                'id': r.id,
                'auteur': r.etudiant.user.first_name,
                'type': r.type_reaction,
                'contrib_id': r.contribution_id,
            } for r in reacts
        ],
    }
    return JsonResponse(data)

