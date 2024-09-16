"""
URL Mappings for Util API Requests.
"""

from django.urls import path
from util import views

urlpatterns = [
    path('suggest-recipe/', views.SuggestRecipeView.as_view(),
         name='suggest-recipe')
]
