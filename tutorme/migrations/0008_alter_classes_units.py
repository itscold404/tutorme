# Generated by Django 4.1.6 on 2023-03-09 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorme', '0007_rename_title_classes_title_classes_section_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='units',
            field=models.CharField(max_length=10),
        ),
    ]
