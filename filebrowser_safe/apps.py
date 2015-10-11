from django.apps import apps, AppConfig
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models.signals import post_migrate


def create_permissions(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, **kwargs):
    try:
        Permission = apps.get_model('auth', 'Permission')
    except LookupError:
        return

    if not router.allow_migrate(using, Permission):
        return

    # create a dummy content type for the app
    from django.contrib.contenttypes.models import ContentType
    appname = 'filebrowser_safe'
    ct, created = ContentType.objects.get_or_create(model='', app_label=appname,
                                                    defaults={'name': appname})

    # create each permission
    permissions = (
        ('upload_file', 'Upload files'),
        ('overwrite_file', 'Overwrite files'),
        ('rename_file', 'Rename files'),
        ('delete_file', 'Delete files'),
    )

    for codename, name in permissions:
        p, created = Permission.objects.get_or_create(codename=codename,
                        content_type__pk=ct.id,
                        defaults={'name': name, 'content_type': ct})


class FilebrowserConfig(AppConfig):
    name = 'filebrowser_safe'

    def ready(self):
        post_migrate.connect(create_permissions,
                             sender=self,
                             dispatch_uid="filebrowser_safe.apps.create_permissions")
