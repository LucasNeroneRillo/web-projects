# Generated by Django 3.2.3 on 2021-06-07 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_listings_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listings',
            name='image_url',
            field=models.URLField(blank=True, max_length=8192),
        ),
    ]
