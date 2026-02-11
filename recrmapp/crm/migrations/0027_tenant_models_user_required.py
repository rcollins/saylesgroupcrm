# Set user to non-nullable after backfill

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0026_backfill_user_on_tenant_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.ForeignKey(
                help_text='User (agent) who owns this client record.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_clients',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(
                help_text='User (agent) who owns this contact record.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_contacts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='lead',
            name='user',
            field=models.ForeignKey(
                help_text='User (agent) who owns this lead record.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='user',
            field=models.ForeignKey(
                help_text='User (agent) who owns this property record.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='crm_properties',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
