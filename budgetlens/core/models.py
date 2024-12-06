"""This module contains the models for the core app."""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Expense(models.Model):
    """Model to store the expense details"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receipt_image = models.ImageField(upload_to="receipts/")
    category = models.CharField(max_length=100, blank=True, null=True)
    expense_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    amount_in_target_currency = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

class UserProfile(models.Model):
    """Model to store the user's profile details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_currency = models.CharField(max_length=3, blank=True, null=True, default="EUR")
    objects = models.Manager()

@receiver(post_save, sender=User)
def create_user_profile(_sender, instance, created, **kwargs):
    """Signal to create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(_sender, instance, **kwargs):
    """Signal to save the user profile when the user is updated"""
    instance.userprofile.save()
