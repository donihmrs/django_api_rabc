# core/urls.py
from django.conf import settings
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, ProductViewSet, OrderViewSet, InvitationViewSet, LogoutView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('logout', LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += [
        path('schema', SpectacularAPIView.as_view(), name='schema'),
        path('docs/swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('docs/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]