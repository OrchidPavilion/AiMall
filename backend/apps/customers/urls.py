from django.urls import path

from .views import (
    AdminCustomerBehaviorsView,
    AdminCustomerDetailView,
    AdminCustomerListView,
    MallAuthLoginView,
    MallAuthProfileView,
    MallAuthRegisterView,
)

urlpatterns = [
    path('admin/customers', AdminCustomerListView.as_view()),
    path('admin/customers/<int:pk>', AdminCustomerDetailView.as_view()),
    path('admin/customers/<int:pk>/behaviors', AdminCustomerBehaviorsView.as_view()),
    path('mall/auth/register', MallAuthRegisterView.as_view()),
    path('mall/auth/login', MallAuthLoginView.as_view()),
    path('mall/auth/profile', MallAuthProfileView.as_view()),
]
