from django.urls import path

from .views import MallCartItemDetailView, MallCartItemsView, MallCartSettlementPreviewView

urlpatterns = [
    path('mall/cart/items', MallCartItemsView.as_view()),
    path('mall/cart/items/<int:pk>', MallCartItemDetailView.as_view()),
    path('mall/cart/settlement-preview', MallCartSettlementPreviewView.as_view()),
]
