# core/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, ProductViewSet, OrderViewSet, InvitationViewSet, LogoutView

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('logout', LogoutView.as_view(), name='logout'),
]
