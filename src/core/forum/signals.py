# main/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Etudiant, Professeur, User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        
        if instance.profile_type == 'etudiant'and not hasattr(instance, 'etudiant_profile'):
            Etudiant.objects.create(user=instance, id_faculte=None, id_promotion=None)
        elif instance.profile_type == 'professeur' and not hasattr(instance, 'prof_profile'):
            Professeur.objects.create(user=instance)
