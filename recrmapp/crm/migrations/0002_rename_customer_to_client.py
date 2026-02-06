# Generated manually for rename Customer -> Client

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(old_name='Customer', new_name='Client'),
        migrations.RenameField(
            model_name='property',
            old_name='customer',
            new_name='client',
        ),
    ]
