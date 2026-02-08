# Generated manually: UserProfile and remove email signature from AppSettings

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0018_remove_choicelist_crm_choicelist_unique_type_code_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_signature', models.TextField(blank=True, help_text='HTML signature appended to your outgoing emails. Use <a href="url"> for links and <img src="url"> for images.')),
                ('signature_image', models.FileField(blank=True, null=True, upload_to='user_profiles/signature/', help_text='Optional image (e.g. logo or photo) shown at the end of your email signature.')),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User profile',
                'verbose_name_plural': 'User profiles',
            },
        ),
        migrations.RemoveField(
            model_name='appsettings',
            name='email_signature',
        ),
        migrations.RemoveField(
            model_name='appsettings',
            name='signature_image',
        ),
    ]
