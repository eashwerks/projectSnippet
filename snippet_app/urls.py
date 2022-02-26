from django.urls import path, include
from rest_framework.routers import DefaultRouter

from snippet_app.views import SnippetViewSet, TagViewSet

router = DefaultRouter()

router.register('snippets', SnippetViewSet)
router.register('tags', TagViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
