# Generated by Django 5.1.1 on 2024-12-07 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password_confirm',
        ),
    ]
