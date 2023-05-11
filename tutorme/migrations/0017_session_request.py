# Generated by Django 4.1.7 on 2023-03-25 05:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutorme', '0016_post_current_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator_email', models.EmailField(max_length=254, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorme.post')),
                ('tutee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorme.person')),
            ],
        ),
    ]