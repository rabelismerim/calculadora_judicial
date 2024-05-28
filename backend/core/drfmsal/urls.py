from django.urls import path

from .views import SignStatusApi, ClearCacheApi, AADRedirectView, SignInView, SignOutView, PostSignOutView

urlpatterns = [
    path('drfmsal_signstatus/', SignStatusApi.as_view()),
    path('cache/', ClearCacheApi.as_view()),
    path('drfmsal_signin/<path:redirect_uri>/', SignInView.as_view(), name='drfmsal_signin'),
    path('drfmsal_redirect/<path:redirect_uri>/', AADRedirectView.as_view(), name='drfmsal_redirect'),
    path('drfmsal_signout/<path:redirect_uri>/', SignOutView.as_view(), name='drfmsal_signout'),
    path('drfmsal_postsignout/<path:redirect_uri>/', PostSignOutView.as_view(), name='drfmsal_postsignout'),
]
