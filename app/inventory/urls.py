"""
URL mappings for inventory views.
"""

from django.urls import path, include
from inventory import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('inventorys', views.InventoryViewSet)

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
]
