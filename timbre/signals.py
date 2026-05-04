from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from timbre.roles import ROLES
from users.models import User
from .models import Notification, Transaction
from django.db import transaction

#update permissions wthen role is assigned    
@receiver(post_save, sender=Transaction)
def send_transction_notif(sender, instance, created, **kwargs):
    if not created:
        user = User.objects.get(pk=instance.timbre.owned_by.id)
        controller = User.objects.get(pk=instance.controller.id)
        Notification.objects.create(content=f"La transation  vers {controller} est {'est accpetée' if instance.status == 'accepted' else 'est rejetée' }",user=user,link={"id":instance.pk})
        Notification.objects.create(content=f"La transation de la part {user} est {'est accpetée' if instance.status == 'accepted' else 'est rejetée' }",user=controller,link={"id":instance.pk})
        return


    def _send():
        user = User.objects.get(pk=instance.timbre.owned_by.id)
        controller = User.objects.get(pk=instance.controller.id)
        Notification.objects.create(content="Une transation est en attente",user=user,link={"id":instance.pk})
        Notification.objects.create(content="Une transation est en attente",user=controller,link={"id":instance.pk})


    # 🔑 exécuté après commit
    transaction.on_commit(_send)