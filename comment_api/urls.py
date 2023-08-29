from django.urls import path
from .views import CommentListCreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CreateUserAPIView


urlpatterns = [
    path('comments/', CommentListCreateAPIView.as_view(), name='comment-create-api'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/registration/', CreateUserAPIView.as_view(), name='create_user'),
]
