# Generated by Django 3.2.3 on 2021-08-12 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_assignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
