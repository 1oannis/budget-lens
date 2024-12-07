from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('upload/', views.upload_receipt, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]
