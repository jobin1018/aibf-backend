# Generated by Django 5.1 on 2025-03-20 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_registration_payment_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='additional_kids',
            new_name='additional_kids_3_8',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='no_of_children',
            new_name='no_of_children_3_8',
        ),
        migrations.AddField(
            model_name='registration',
            name='additional_kids_9_13',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='no_of_children_9_13',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='selected_package',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
