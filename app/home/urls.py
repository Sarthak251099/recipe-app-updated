"""
URL mappings for home API.
"""

from django.urls import path, include
from home import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('homes', views.HomeViewSet)
router.register('inventorys', views.InventoryViewSet)

app_name = 'home'

urlpatterns = [
    path('', include(router.urls)),
]
