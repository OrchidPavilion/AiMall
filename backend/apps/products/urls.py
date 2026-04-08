from django.urls import path

from .views import (
    AdminProductDetailView,
    AdminProductListView,
    AdminProductStatusView,
    AdminProductUploadView,
    MallProductDetailView,
    MallProductListView,
    MallProductRandomView,
)

urlpatterns = [
    path('admin/products', AdminProductListView.as_view()),
    path('admin/products/<int:pk>', AdminProductDetailView.as_view()),
    path('admin/products/<int:pk>/status', AdminProductStatusView.as_view()),
    path('admin/upload/image', AdminProductUploadView.as_view()),
    path('mall/products', MallProductListView.as_view()),
    path('mall/products/random', MallProductRandomView.as_view()),
    path('mall/products/<int:pk>', MallProductDetailView.as_view()),
]
