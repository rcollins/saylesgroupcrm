# Generated migration for newsletter_opt_in (sync to Mailchimp/Constant Contact)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0021_userprofile_mailchimp_constant_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='newsletter_opt_in',
            field=models.BooleanField(default=False, help_text='Include in newsletter sync to Mailchimp/Constant Contact when opted in.'),
        ),
        migrations.AddField(
            model_name='lead',
            name='newsletter_opt_in',
            field=models.BooleanField(default=False, help_text='Include in newsletter sync to Mailchimp/Constant Contact when opted in.'),
        ),
        migrations.AddField(
            model_name='contact',
            name='newsletter_opt_in',
            field=models.BooleanField(default=False, help_text='Include in newsletter sync to Mailchimp/Constant Contact when opted in.'),
        ),
    ]
