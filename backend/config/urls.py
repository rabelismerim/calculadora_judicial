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
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import include, path, re_path, reverse
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from config.settings import ENABLE_SSO, IS_LOCALHOST, BASE_URL_NEXT
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.schemas import get_schema_view
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.conf.urls.static import static
from django.contrib.auth import views, logout
from config.settings import BASE_URL, BASE_URL_AUTH
from rest_framework.authtoken import views as rest_views

admin.site.site_header = admin.site.site_title = 'JUCA'
admin.site.index_title = 'Administration area'
admin.site.site_url = '/juca/admin/login'


@ensure_csrf_cookie
def frontend_index(request):
    if request.META.get('REQUEST_URI', 'none')[:5].upper() == '/juca':
        return HttpResponseRedirect("/")
    else:
        return render(request, template_name='index.html')


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logout(request)
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
def post_logout(request):
    logout(request)
    return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    # API Authentication
    path('juca/api-auth/', include("rest_framework.urls")),

    # # Projects
    path(f'{BASE_URL}projects/', include(("projects.urls.current", 'v1'), namespace='teste')),
    path(f'{BASE_URL_NEXT}projects/', include(("projects.urls.next", 'v2'), namespace='teste2')),
    #
    # # # Recovering
    # path(f'{BASE_URL}recovering/', include("recovering.urls.current")),
    # path(f'{BASE_URL_NEXT}recovering/', include("recovering.urls.next")),
    #
    # # Creditors
    # path(f'{BASE_URL}creditors/', include("creditors.urls")),

    # File
    path(f'{BASE_URL}base/', include("base.urls")),
    path(f'{BASE_URL}file/', include("file.urls")),

    # # Calculation
    # path(f'{BASE_URL}calculation/', include("calculation.urls.current")),
    # path(f'{BASE_URL_NEXT}calculation/', include("calculation.urls.next")),
    #
    # # Rates
    # path(f'{BASE_URL}rates/', include("rates.urls")),
    #
    # # Big Numbers
    # path(f'{BASE_URL}big_number/', include("big_number.urls")),

    # CORE
    path(BASE_URL, include("core.dttuser.api.urls")),

    # TODO: desativar urls sem versão de api
    path(BASE_URL_AUTH, include("core.drfmsal.urls")),
    path(BASE_URL_AUTH, include("core.dttuser.urls")),

    path(BASE_URL, include("core.drfmsal.urls")),
    path(BASE_URL, include("core.dttuser.urls")),

    # Django
    path('juca/admin/', admin.site.urls),
    path('juca/login/', views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('juca/logout/', views.LogoutView.as_view(), name='logout'),

    # VUE FRONTEND
    re_path(r'^(?!juca\/admin|juca\/api|simple|juca\/media).*$', frontend_index, name='frontend'),
    # re_path(f'{BASE_URL}logout/', post_logout, name='api-logout'),

    re_path(f'{BASE_URL}logout/', LogoutView.as_view(), name='api-logout'),
    # path('juca/<path:resource>', frontend_index, name='frontend'),

    # Documentation
    path(f'{BASE_URL}docs/swagger/', TemplateView.as_view(template_name='api_docs.html',
                                                          extra_context={'schema_url': 'schema-api'}), name='JUCA'),
    path(f'{BASE_URL}docs/redoc/', get_schema_view(title="Deloitte JUCA Project",
                                                   description="System that integrates the legal, calculation and "
                                                               "financial teams of RJ / Bankruptcy processes ("
                                                               "liabilities monitoring)",
                                                   version="1.0.0", permission_classes=[permissions.AllowAny]),
         name='schema-api'),
]

# TODO: definir se frontend MFA pode ter alteração de versões
# Active or inactive MFA login MS
if IS_LOCALHOST is False:
    urlpatterns.extend([
        path('juca/admin/login/', lambda r: redirect(
            reverse('drfmsal_signin', kwargs={'redirect_uri': 'juca/admin'})
        )),
        path('juca/admin/logout/', lambda r: redirect(
            reverse('drfmsal_signout', kwargs={'redirect_uri': 'juca'})
        )),
    ])

if ENABLE_SSO is False:
    urlpatterns.extend([
        path(f'{BASE_URL}obtain-auth-token/', rest_views.obtain_auth_token),
    ])

# if IS_LOCALHOST or BRANCH_LOCAL:
#     urlpatterns.extend([])

# if (str(os.getenv('ENV', )) == 'branch') or (str(os.getenv('ENV')) == 'hml'):
#     urlpatterns += static(f"/juca" + settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(f"/juca" + settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
