from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.AIChatView.as_view(), name="ai-chat"),
    path("recommend/", views.AIRecommendView.as_view(), name="ai-recommend"),
]