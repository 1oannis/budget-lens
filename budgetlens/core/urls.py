from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_receipt, name='upload'),  # For uploading receipts via core/upload
    path('dashboard/', views.dashboard, name='dashboard'),  # For viewing the dashboard via core/dashboard
]
