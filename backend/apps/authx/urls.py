from django.urls import path

from .views import AdminLoginView, AdminLogoutView, AdminProfileView

urlpatterns = [
    path('login', AdminLoginView.as_view()),
    path('logout', AdminLogoutView.as_view()),
    path('profile', AdminProfileView.as_view()),
]
