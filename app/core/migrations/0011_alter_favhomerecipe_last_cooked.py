# Generated by Django 3.2.25 on 2024-09-12 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20240912_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favhomerecipe',
            name='last_cooked',
            field=models.DateField(blank=True, null=True),
        ),
    ]
