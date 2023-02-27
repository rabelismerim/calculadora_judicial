"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import os
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path, re_path, reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from config.settings import ENABLE_SSO, IS_LOCALHOST
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.schemas import get_schema_view, AutoSchema
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf.urls.static import static
from django.contrib.auth import views
from config.settings import BASE_URL, BASE_URL_AUTH
from rest_framework.authtoken import views as rest_views

admin.site.site_header = admin.site.site_title = 'DJUD'
admin.site.index_title = 'Administration area'
admin.site.site_url = '/djud/admin/login'


@ensure_csrf_cookie
def frontend_index(request):
    if request.META.get('REQUEST_URI', 'none')[:5].upper() == '/DJUD':
        return HttpResponseRedirect("/")
    else:
        return render(request, template_name='index.html')


urlpatterns = [
    # API Authentication
    path('djud/api-auth/', include("rest_framework.urls")),

    # # Base
    path(f'{BASE_URL}base/', include("base.urls")),

    # # Projects
    path(f'{BASE_URL}projects/', include("projects.urls")),

    # # Recovering
    path(f'{BASE_URL}recovering/', include("recovering.urls")),

    # Creditors
    path(f'{BASE_URL}creditors/', include("creditors.urls")),

    # Calculation
    path(f'{BASE_URL}calculation/', include("calculation.urls")),

    # Rates
    path(f'{BASE_URL}rates/', include("rates.urls")),

    # CORE
    path(BASE_URL, include("core.dttuser.api.urls")),
    path(BASE_URL_AUTH, include("core.drfmsal.urls")),
    path(BASE_URL_AUTH, include("core.dttuser.urls")),

    # Django
    path('djud/admin/', admin.site.urls),
    path('djud/login/', views.LoginView.as_view()),
    path('djud/logout/', views.LogoutView.as_view()),

    # VUE FRONTEND
    re_path(r'^(?!djud\/admin|djud\/api).*$', frontend_index, name='frontend'),
    # path('djud/<path:resource>', frontend_index, name='frontend'),

    # Documentation
    path(f'{BASE_URL}docs/swagger/', TemplateView.as_view(template_name='api_docs.html',
         extra_context={'schema_url': 'schema-api'}), name='DJUD'),
    path(f'{BASE_URL}docs/redoc/', get_schema_view(title="Deloitte DJUD Project", description="System that integrates the legal, calculation and financial teams of RJ / Bankruptcy processes (liabilities monitoring)",
         version="1.0.0", permission_classes=[permissions.AllowAny]), name='schema-api'),
]

# TODO: definir se frontend MFA pode ter alteração de versões
# Active or inactive MFA login MS
if IS_LOCALHOST is False:
    urlpatterns.extend([
        path('djud/admin/login/', lambda r: redirect(
            reverse('drfmsal_signin', kwargs={'redirect_uri': 'djud/admin'})
        )),
        path('djud/admin/logout/', lambda r: redirect(
            reverse('drfmsal_signout', kwargs={'redirect_uri': 'djud'})
        )),
    ])

if ENABLE_SSO is False:
    urlpatterns.extend([
        path(f'{BASE_URL}obtain-auth-token/', rest_views.obtain_auth_token),
    ])

# if IS_LOCALHOST or BRANCH_LOCAL:
#     urlpatterns.extend([])

if (str(os.getenv('ENV', )) == 'branch') or (str(os.getenv('ENV')) == 'hml'):
    urlpatterns += static("/djud"+settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
