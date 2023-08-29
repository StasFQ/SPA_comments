from django.urls import path, include

from .views import RegisterFormPage

urlpatterns = [
    path('', RegisterFormPage.as_view(), name='RegisterFormPage'),
    path('authentificate/', include('django.contrib.auth.urls')),
]
