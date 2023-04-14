from django.urls import path

from .views import sign_in, aad_redirect, sign_out, post_sign_out, SignStatusApi

urlpatterns = [
    # path('drfmsal_signstatus/', sign_status, name='drfmsal_signstatus'),
    path('drfmsal_signstatus/', SignStatusApi.as_view()),
    path('drfmsal_signin/<path:redirect_uri>/', sign_in, name='drfmsal_signin'),
    path('drfmsal_redirect/<path:redirect_uri>/', aad_redirect, name='drfmsal_redirect'),
    path('drfmsal_signout/<path:redirect_uri>/', sign_out, name='drfmsal_signout'),
    path('drfmsal_postsignout/<path:redirect_uri>/', post_sign_out, name='drfmsal_postsignout'),
]
