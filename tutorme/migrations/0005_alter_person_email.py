# Generated by Django 4.1.6 on 2023-03-07 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorme', '0004_person_post_delete_tutee_delete_tutor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]