# Generated by Django 3.2.25 on 2024-09-12 13:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_favhomerecipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favhomerecipe',
            name='rating',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)]),
        ),
    ]
