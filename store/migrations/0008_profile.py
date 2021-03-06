# Generated by Django 3.2.3 on 2021-12-18 15:10

import annoying.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('store', '0007_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('phone', models.CharField(max_length=200, null=True)),
                ('profile_pic', models.ImageField(blank=True, default='avatar/anna.jpg', null=True, upload_to='avatar')),
            ],
        ),
    ]
