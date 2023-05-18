"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from comment import views
    2. Add a URL to urlpatterns:  path('', views.CommentApi, name='comment')
Class-based views
    1. Add an import:  from comment import Comment
    2. Add a URL to urlpatterns:  path('', CommentApi.as_view(), name='comment')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('comment/', include('comment.another_app.urls'))
"""
from django.urls import path
from .views import CommentApi


urlpatterns = [
    path('', CommentApi.as_view(), name="comment-list-create"),
]
