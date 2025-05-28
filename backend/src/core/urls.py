"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.auth.urls import router as auth_router

# from apps.users.urls import router as user_router

urlpatterns_non_i18n = [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # path('admin/', admin.site.urls),
]

urlpatterns_i18n = i18n_patterns(
    # API V1 URLs
    path(_("api-auth/"), include("rest_framework.urls")),
    path(_("api/v1/auth/"), include(auth_router.urls)),
    # path("api/v1/users/", include(user_router.urls)),
    # path("api/v1/auth/", include("dj_rest_auth.urls")),
    # path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("api/v1/notifications/", include("apps.notifications.urls")),
    # prefix_default_language=False # Opcjonalnie
)

urlpatterns = urlpatterns_non_i18n + urlpatterns_i18n
if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
