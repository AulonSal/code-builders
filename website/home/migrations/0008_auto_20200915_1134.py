# Generated by Django 3.1.1 on 2020-09-15 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20200910_2329'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventcategory',
            old_name='type',
            new_name='name',
        ),
    ]
