# Generated by Django 5.1.2 on 2024-12-11 09:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_expense_created_at_expense_updated_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="amount_in_target_currency",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="expense",
            name="category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Housing", "Housing"),
                    ("Utilities", "Utilities"),
                    ("Transportation", "Transportation"),
                    ("Groceries", "Groceries"),
                    ("Dining Out", "Dining Out"),
                    ("Healthcare", "Healthcare"),
                    ("Debt Payments", "Debt Payments"),
                    ("Insurance", "Insurance"),
                    ("Clothing", "Clothing"),
                    ("Entertainment", "Entertainment"),
                    ("Education", "Education"),
                    ("Childcare", "Childcare"),
                    ("Pet Care", "Pet Care"),
                    ("Subscriptions", "Subscriptions"),
                    ("Miscellaneous", "Miscellaneous"),
                ],
                max_length=100,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "target_currency",
                    models.CharField(
                        blank=True, default="EUR", max_length=3, null=True
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
