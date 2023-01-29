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
from django.contrib import admin
from django.urls import include, path, re_path, reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from config.settings import IS_LOCALHOST

from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.schemas import get_schema_view

from django.views.decorators.csrf import ensure_csrf_cookie
import os


admin.site.site_header = admin.site.site_title = 'aplication'
admin.site.index_title = 'Administration area'
admin.site.site_url = '/aplication/admin/login'

@ensure_csrf_cookie
def frontend_index(request):
    return render(request, template_name='index.html')

base_url = 'aplication/api/v1/'
base_url_auth = 'aplication/api/'
urlpatterns = [
    path('aplication/api-auth/', include("rest_framework.urls")),  
    path(f'{base_url}projects/', include("projects.urls")),
    path(base_url, include("core.drfmsal.urls")),
    path(base_url, include("core.dttuser.urls")),
    
    # VUE FRONTEND
    re_path(r'^(?!aplication\/static|aplication\/admin|aplication\/api).*$', frontend_index, name='frontend'),
    path(base_url_auth, include("core.dttuser.api.urls")),

    path(f'{base_url}docs/',
         TemplateView.as_view(template_name='api_docs.html', extra_context={'schema_url': 'schema-api'}), name='api-docs'),
    path(f'{base_url}docs/deloitte/', get_schema_view(title="Project Deloitte DJUD",
                                                  description="Api for Djud platform",
                                                  version="1.0.0", permission_classes=[permissions.AllowAny]),
         name='schema-api'),
]

# TODO: definir se frontend MFA pode ter auteração de versões
# Active or inactive MFA login MS
if IS_LOCALHOST:
    urlpatterns.extend([path('aplication/admin/', admin.site.urls),])
else:
    urlpatterns.extend([
        path('aplication/admin/login/', lambda r: redirect(
        reverse('drfmsal_signin', kwargs={'redirect_uri': 'aplication/admin'})
    )),
    path('aplication/admin/logout/', lambda r: redirect(
        reverse('drfmsal_signout', kwargs={'redirect_uri': 'aplication'})
    )),
    ])
    

# adds image to urlpath
from django.conf.urls.static import static
from django.conf import settings

if (str(os.getenv('ENV', )) == 'branch') or (str(os.getenv('ENV')) == 'hml'):
    urlpatterns += static("aplication"+settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)