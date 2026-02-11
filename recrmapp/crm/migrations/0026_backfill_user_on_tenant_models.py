# Data migration: assign existing records to first user so we can set null=False

from django.db import migrations


def backfill_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    first_user = User.objects.order_by('pk').first()
    if not first_user:
        return
    Client = apps.get_model('crm', 'Client')
    Lead = apps.get_model('crm', 'Lead')
    Contact = apps.get_model('crm', 'Contact')
    Property = apps.get_model('crm', 'Property')
    Client.objects.filter(user__isnull=True).update(user_id=first_user.pk)
    Lead.objects.filter(user__isnull=True).update(user_id=first_user.pk)
    Contact.objects.filter(user__isnull=True).update(user_id=first_user.pk)
    Property.objects.filter(user__isnull=True).update(user_id=first_user.pk)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0025_add_user_to_tenant_models'),
    ]

    operations = [
        migrations.RunPython(backfill_user, noop),
    ]
