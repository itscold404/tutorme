# Generated by Django 3.2.17 on 2023-02-23 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorme', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutee',
            name='password',
            field=models.CharField(default='password', max_length=50),
        ),
        migrations.AddField(
            model_name='tutor',
            name='password',
            field=models.CharField(default='password', max_length=50),
        ),
    ]
