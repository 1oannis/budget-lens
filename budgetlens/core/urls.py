from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Define the index URL pattern
    path('upload/', views.upload_receipt, name='upload_receipt'),  # For uploading receipts
    path('receipt/<uuid:receipt_id>/', views.receipt_detail, name='receipt_detail'),  # For viewing receipt details
]
