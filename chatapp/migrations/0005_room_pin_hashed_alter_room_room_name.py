# Generated by Django 5.2.2 on 2025-06-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatapp', '0004_message_message_hash_message_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='pin_hashed',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
