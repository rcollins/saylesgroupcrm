# Generated migration for Mailchimp / Constant Contact connection on UserProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_appsettings_inactivity_timeout_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mailchimp_api_key',
            field=models.CharField(blank=True, help_text='Mailchimp API key (Account → Extras → API keys). Leave blank to keep current or disable.', max_length=100),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mailchimp_audience_id',
            field=models.CharField(blank=True, help_text='Mailchimp Audience (list) ID from Audience → Settings.', max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='constant_contact_api_key',
            field=models.CharField(blank=True, help_text='Constant Contact App Key (client ID from developer portal).', max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='constant_contact_api_secret',
            field=models.CharField(blank=True, help_text='Constant Contact App Secret. Leave blank to keep current.', max_length=200),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='constant_contact_access_token',
            field=models.TextField(blank=True, help_text='Constant Contact OAuth2 access token. Leave blank to keep current.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='constant_contact_refresh_token',
            field=models.TextField(blank=True, help_text='Constant Contact OAuth2 refresh token. Leave blank to keep current.'),
        ),
    ]
