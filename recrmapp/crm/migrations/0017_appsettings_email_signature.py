# Generated manually for email signature and signature_image on AppSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_property_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='email_signature',
            field=models.TextField(
                blank=True,
                help_text='HTML signature appended to outgoing emails. Use <a href="url"> for links and <img src="url"> for images.',
            ),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='signature_image',
            field=models.FileField(
                blank=True,
                help_text='Optional image (e.g. logo or photo) shown at the end of the email signature.',
                null=True,
                upload_to='app_admin/signature/',
            ),
        ),
    ]
