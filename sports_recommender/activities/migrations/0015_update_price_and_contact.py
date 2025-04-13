from django.db import migrations

def update_price_and_contact(apps, schema_editor):
    Activity = apps.get_model('activities', 'Activity')
    Activity.objects.all().update(
        price_range='$1.80 - $9.00',
        contact_info='85993729'
    )

def revert_price_and_contact(apps, schema_editor):
    Activity = apps.get_model('activities', 'Activity')
    Activity.objects.all().update(
        price_range='$',
        contact_info=''
    )

class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0014_merge_20250414_0106'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.RunPython(update_price_and_contact, revert_price_and_contact),
    ] 