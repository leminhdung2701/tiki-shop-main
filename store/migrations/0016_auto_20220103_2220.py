# Generated by Django 3.2.3 on 2022-01-03 15:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0015_auto_20220103_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='user_likes',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
