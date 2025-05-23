# Generated by Django 4.2.19 on 2025-04-30 00:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_alter_book_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="rating",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=3,
                validators=[
                    django.core.validators.MinValueValidator(1.0),
                    django.core.validators.MaxValueValidator(5.0),
                ],
            ),
        ),
    ]
