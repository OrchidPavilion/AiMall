from django.urls import path

from .views import MallHomeView

urlpatterns = [
    path('mall/home', MallHomeView.as_view()),
]
