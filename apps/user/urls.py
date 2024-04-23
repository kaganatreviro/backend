from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView
)

from .views import UserViewSet, ClientRegisterView, CreatePartner

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(
        'client_register/', ClientRegisterView.as_view(),
        name='client-register'
    ),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('create_partner/', CreatePartner.as_view(), name='create-partner'),
    path('<int:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    })),
]