# Add Constant Contact list ID for sync target

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0022_newsletter_opt_in'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='constant_contact_list_id',
            field=models.CharField(blank=True, help_text='Constant Contact list ID to add synced contacts to (required for sync).', max_length=100),
        ),
    ]
