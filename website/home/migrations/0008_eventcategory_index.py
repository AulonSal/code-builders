# Generated by Django 3.1.1 on 2020-09-15 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20200910_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcategory',
            name='index',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]