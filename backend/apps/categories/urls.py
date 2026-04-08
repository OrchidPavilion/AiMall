from django.urls import path

from .views import AdminCategoryDetailView, AdminCategoryTreeView, MallCategoryTreeView

urlpatterns = [
    path('admin/categories/tree', AdminCategoryTreeView.as_view()),
    path('admin/categories', AdminCategoryTreeView.as_view()),
    path('admin/categories/<int:pk>', AdminCategoryDetailView.as_view()),
    path('mall/categories/tree', MallCategoryTreeView.as_view()),
]
