from django.urls import path

from .views import MallBehaviorCreateView

urlpatterns = [
    path('mall/behaviors', MallBehaviorCreateView.as_view()),
]
