from django.urls import path

from .views import (
    AdminRecommendationListView,
    AdminRecommendationRefreshView,
    AdminRecommendationSettingView,
    AdminRecommendationDataAnalysisView,
    AdminRecommendationExperimentRunView,
    AdminRecommendationExperimentDetailView,
    AdminRecommendationExperimentExportView,
    AdminRecommendationBehaviorReplayView,
    AdminRecommendationBehaviorResetView,
    AdminCustomerRecommendationCompareView,
    MallRecommendationListView,
)

urlpatterns = [
    path('admin/recommendations', AdminRecommendationListView.as_view()),
    path('admin/recommendations/refresh', AdminRecommendationRefreshView.as_view()),
    path('admin/recommendation-settings', AdminRecommendationSettingView.as_view()),
    path('admin/recommendations/analysis', AdminRecommendationDataAnalysisView.as_view()),
    path('admin/recommendations/experiments', AdminRecommendationExperimentRunView.as_view()),
    path('admin/recommendations/experiments/<int:pk>', AdminRecommendationExperimentDetailView.as_view()),
    path('admin/recommendations/experiments/<int:pk>/export', AdminRecommendationExperimentExportView.as_view()),
    path('admin/recommendations/behavior-replay', AdminRecommendationBehaviorReplayView.as_view()),
    path('admin/recommendations/behavior-reset', AdminRecommendationBehaviorResetView.as_view()),
    path('admin/customers/<int:pk>/recommendation-compare', AdminCustomerRecommendationCompareView.as_view()),
    path('mall/recommendations', MallRecommendationListView.as_view()),
]
