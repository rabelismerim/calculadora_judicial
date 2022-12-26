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
from django.views.generic import TemplateView, RedirectView
import os


admin.site.site_header = admin.site.site_title = 'aplication'
admin.site.index_title = 'Administration area'
admin.site.site_url = '/aplication'

def frontend_index(request):
    return render(request, template_name='index.html')

urlpatterns = [
    path('aplication/admin/login/', lambda r: redirect(
        reverse('drfmsal_signin', kwargs={'redirect_uri': 'aplication/admin'})
    )),
    path('aplication/admin/logout/', lambda r: redirect(
        reverse('drfmsal_signout', kwargs={'redirect_uri': 'aplication'})
    )),
    path('aplication/admin/', admin.site.urls),
    path('aplication/api-auth/', include("rest_framework.urls")),  
    path('aplication/api/', include("projetos.urls")),
    path('aplication/api/', include("core.drfmsal.urls")),
    
    # VUE FRONTEND
    re_path(r'^(?!aplication\/static|aplication\/admin|aplication\/api).*$', frontend_index, name='frontend'),
    path('aplication/api/', include("core.dttuser.api.urls")),
]


# adds image to urlpath
from django.conf.urls.static import static
from django.conf import settings

if (str(os.getenv('ENV')) == 'branch') or (str(os.getenv('ENV')) == 'hml'):
    urlpatterns += static("aplication"+settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)