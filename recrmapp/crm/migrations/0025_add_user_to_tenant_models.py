# Generated manually for multi-user tenant isolation

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0024_merge_20260210_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='User (agent) who owns this client record.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_clients',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='User (agent) who owns this contact record.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_contacts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='User (agent) who owns this lead record.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='User (agent) who owns this property record.',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_properties',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
