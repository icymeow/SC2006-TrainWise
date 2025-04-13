from django.db import migrations

def add_activity_images(apps, schema_editor):
    Activity = apps.get_model('activities', 'Activity')
    
    # Update swimming activities
    Activity.objects.filter(activity_type='SWIMMING').update(
        image_url='https://images.unsplash.com/photo-1519315901367-f34ff9154487?w=500'
    )
    
    # Update gym activities
    Activity.objects.filter(activity_type='GYM').update(
        image_url='https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500'
    )
    
    # Update running activities
    Activity.objects.filter(activity_type='RUNNING').update(
        image_url='https://images.unsplash.com/photo-1538503657467-6ccca16dc10e?w=500'
    )
    
    # Update basketball activities
    Activity.objects.filter(activity_type='BASKETBALL').update(
        image_url='https://images.unsplash.com/photo-1546519638-68e109498ffc?w=500'
    )
    
    # Update football activities
    Activity.objects.filter(activity_type='FOOTBALL').update(
        image_url='https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=500'
    )
    
    # Update tennis activities
    Activity.objects.filter(activity_type='TENNIS').update(
        image_url='https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=500'
    )

def remove_activity_images(apps, schema_editor):
    Activity = apps.get_model('activities', 'Activity')
    Activity.objects.all().update(image_url='')

class Migration(migrations.Migration):
    dependencies = [
        ('activities', '0003_remove_userpreference_preferred_intensity_and_more'),
    ]

    operations = [
        migrations.RunPython(add_activity_images, remove_activity_images),
    ] 