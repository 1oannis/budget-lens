"""This module contains the models for the core app."""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Expense(models.Model):
    """Model to store the expense details"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receipt_image = models.ImageField(upload_to="receipts/")
    expense_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    amount_in_target_currency = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    BASE_CATEGORIES = [
        "Housing", "Utilities", "Transportation", "Groceries", "Dining Out", "Healthcare",
        "Debt Payments", "Insurance", "Clothing", "Entertainment", "Education", "Childcare",
        "Pet Care", "Subscriptions", "Miscellaneous"
    ]

    # Create choices for the category field
    CATEGORY_CHOICES = [(category, category) for category in BASE_CATEGORIES]

    # Update the category field to use choices
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.category} - {self.amount} {self.currency} on {self.expense_date}"

class UserProfile(models.Model):
    """Model to store the user's profile details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_currency = models.CharField(max_length=3, blank=True, null=True, default="EUR")
    objects = models.Manager()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal to save the user profile when the user is updated"""
    instance.userprofile.save()
