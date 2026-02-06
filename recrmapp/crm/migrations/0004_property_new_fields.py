# Generated manually for Property model updates

from django.db import migrations, models
import django.db.models.deletion


def migrate_property_status(apps, schema_editor):
    """Map old status values to new choices."""
    Property = apps.get_model('crm', 'Property')
    Property.objects.filter(status='pending').update(status='under_contract')
    Property.objects.filter(status='withdrawn').update(status='off_market')


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_client_new_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='title',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='lot_size',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='year_built',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='mls_number',
            field=models.CharField(blank=True, help_text='MLS listing number', max_length=50),
        ),
        migrations.AddField(
            model_name='property',
            name='mls_service',
            field=models.CharField(
                blank=True,
                choices=[
                    ('bareis', 'BAREIS'),
                    ('paragon', 'Paragon'),
                    ('matrix', 'Matrix'),
                    ('mlslistings', 'MLSListings'),
                    ('redfin', 'Redfin'),
                    ('zillow', 'Zillow'),
                    ('realtor', 'Realtor.com'),
                    ('other', 'Other'),
                ],
                help_text='MLS service provider',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='mls_url',
            field=models.URLField(blank=True, help_text='Direct link to MLS listing'),
        ),
        migrations.AddField(
            model_name='property',
            name='photo',
            field=models.FileField(
                blank=True,
                help_text='Main property photo',
                null=True,
                upload_to='property_photos/',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='property',
            name='features',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='property',
            name='images',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='property',
            name='featured',
            field=models.BooleanField(default=False, help_text='Mark this property as featured'),
        ),
        migrations.RunPython(migrate_property_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='property',
            name='zip_code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.CharField(
                choices=[
                    ('apartment', 'Apartment'),
                    ('commercial', 'Commercial'),
                    ('condo', 'Condo'),
                    ('duplex', 'Duplex'),
                    ('fourplex', 'Fourplex'),
                    ('land', 'Land'),
                    ('mobile_home', 'Mobile Home'),
                    ('single_family', 'Single Family'),
                    ('townhouse', 'Townhouse'),
                    ('triplex', 'Triplex'),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='status',
            field=models.CharField(
                choices=[
                    ('available', 'Available'),
                    ('under_contract', 'Under Contract'),
                    ('sold', 'Sold'),
                    ('off_market', 'Off Market'),
                ],
                default='available',
                max_length=20,
            ),
        ),
        migrations.RenameField(
            model_name='property',
            old_name='client',
            new_name='owner',
        ),
        migrations.AlterField(
            model_name='property',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='properties',
                to='crm.client',
            ),
        ),
        migrations.RemoveField(
            model_name='property',
            name='notes',
        ),
    ]
