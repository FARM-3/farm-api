"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

def redirect_to_docs(request):
    # This sends the user from the root path (/) to your documentation
    return redirect('api/docs/') 

urlpatterns = [
    path('', redirect_to_docs),
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('production.urls')),  # CRITICAL: Must come FIRST - harvests and blocks endpoints
    path('api/', include('financialmanagement.urls')),  # Financial management endpoints
    path('api/aggregation/', include('aggregation.urls')),
    path('api/processing/', include('processing.urls')),
    path('api/users/', include('users.urls')),  # Include users app URLs
    path('api/adminuser/', include('adminuser.urls')),  # Include adminuser app URLs for admin authentication
    path('api/tasks/', include('taskmanagement.urls')),  # Include taskmanagement app URLs
    path('api/activities/', include('activities.urls')),  # Include activities app URLs for activity logging
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), # API schema (to view apis for frontend)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Swagger UI for API docs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve static files during development and in production if DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Available endpoints for users app:
    # - POST /api/users/login/
    # - POST /api/users/security-question/
    # - POST /api/users/reset-pin/
    # - POST /api/users/token/refresh/
    # - GET  /api/users/me/ 
