"""
URL mappings for home API.
"""

from django.urls import path, include
from home import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('homes', views.HomeViewSet)
app_name = 'home'

urlpatterns = [
     path('', include(router.urls)),
     path('inventory-fetch/',
          views.InventoryFetchView.as_view(),
          name='inventory-fetch'),
     path('inventory-create/',
          views.InventoryCreateView.as_view(),
          name='inventory-create'),
     path('inventory-detail/<int:pk>/',
          views.InventoryDetailView.as_view(),
          name='inventory-detail'),
     path('adduser/', views.AddUserToHomeView.as_view(),
          name='adduser'),
     path('remove-home/', views.RemoveUserFromHomeView.as_view(),
          name='remove-home'),
     path('fav-recipes/', views.FavHomeRecipeListView.as_view(),
          name='fav-recipes'),
     path('fav-recipe-create/', views.FavHomeRecipeCreateView.as_view(),
          name='fav-recipe-create'),
     path('fav-recipe-update/<int:pk>/',
          views.FavHomeRecipeUpdateView.as_view(),
          name='fav-recipe-update'),
]
