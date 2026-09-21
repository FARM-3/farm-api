from django.core.management.base import BaseCommand
from users.models import User, RolePermission

DEFAULTS = {
    'admin': {'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': True},
    'manager': {'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': False},
    'block_champion': {'can_view': True, 'can_create': True, 'can_edit': False, 'can_delete': False},
}

MODULES = [m[0] for m in RolePermission.MODULES]


class Command(BaseCommand):
    help = 'Seed default role permissions'

    def handle(self, *args, **options):
        for role, perms in DEFAULTS.items():
            for module in MODULES:
                RolePermission.objects.get_or_create(
                    role=role, module=module,
                    defaults=perms,
                )
        self.stdout.write(self.style.SUCCESS('Permissions seeded'))
