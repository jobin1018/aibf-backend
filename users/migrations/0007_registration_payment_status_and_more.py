# Generated by Django 5.1 on 2025-01-28 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_registration_emails_of_additional_attendees_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together={('event', 'user')},
        ),
    ]
