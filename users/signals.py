from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from timbre.roles import ROLES
from .models import User
from django.db import transaction

#update permissions wthen role is assigned    
@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    role = instance.role
    # print("Assigning permissions for role:", role)
    if created:
        if instance.is_superuser:
            instance.role = "admin"

    if role not in ROLES:
        return
    # print("Assigning permissions for role:==========================================")  

    def _assign():
        user = User.objects.get(pk=instance.pk)

        group, _ = Group.objects.get_or_create(name=role)
        perms = Permission.objects.filter(codename__in=ROLES[role])

        group.permissions.set(perms)

        user.groups.clear()
        user.groups.add(group)
        # print("Permissions:",user.groups.first().permissions.all()) 

    # 🔑 exécuté après commit
    transaction.on_commit(_assign)