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
         name='inventory-create')
]
