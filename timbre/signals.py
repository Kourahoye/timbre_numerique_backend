from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
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
        status_text = _("transaction.isAccepted") if instance.status == 'accepted' else _("transaction.isRejected")
        Notification.objects.create(
            title=_("Transaction"),
            content=f"{_("transaction.to")} {controller} {status_text}",
            user=user,
            link={"id": instance.pk}
        )
        Notification.objects.create(
            title=_("Transaction"),
            content=f"{_("transaction.from")} {user} {status_text}",
            user=controller,
            link={"id": instance.pk}
        )
        return


    def _send():
        user = User.objects.get(pk=instance.timbre.owned_by.id)
        controller = User.objects.get(pk=instance.controller.id)
        Notification.objects.create(
            title=_("Transaction"),
            content=_("transaction.pending"),
            user=user,
            link={"id": instance.pk}
        )
        Notification.objects.create(
            title=_("Transaction"),
            content=_("transaction.pending"),
            user=controller,
            link={"id": instance.pk}
        )


    # 🔑 exécuté après commit
    transaction.on_commit(_send)