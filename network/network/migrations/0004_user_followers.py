# Generated by Django 3.2.3 on 2021-06-16 20:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_alter_post_likers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='_network_user_followers_+', to=settings.AUTH_USER_MODEL),
        ),
    ]