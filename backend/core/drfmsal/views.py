from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from config.settings import ENABLE_SSO

from core.dttuser.models import User

ms_identity_web = settings.DRFMSAL_IDENTITY_WEB


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def sign_status(request):
    if ENABLE_SSO and ms_identity_web.id_data:
        user_view = User.objects.filter(email=ms_identity_web.id_data.usermail)
        if ms_identity_web.id_data.usermail != None:
            if len(user_view) == 0:
                user = User()
                user.email = ms_identity_web.id_data.usermail
                user.password = ms_identity_web.id_data.password
                user.username = ms_identity_web.id_data.username.replace(' ', '_')
                user.first_name = ms_identity_web.id_data.username.split()[0]
                user.last_name = ms_identity_web.id_data.username.split(
                )[len(request.identity_context_data.username.split()) - 1]
                user.is_active = False
                user.status = user.get_status_pending()
                user.userpicture = ms_identity_web.id_data.userpicture
                user.is_staff = False
                user.save()
            elif len(user_view) > 0:
                for item in user_view:
                    if item.userpicture != ms_identity_web.id_data.userpicture:
                        item.userpicture = ms_identity_web.id_data.userpicture
                        item.save()
    return Response()


@require_GET
def sign_in(request, redirect_uri):
    if ENABLE_SSO:
        auth_url = ms_identity_web.get_auth_url(
            redirect_uri=request.build_absolute_uri(
                reverse('drfmsal_redirect', kwargs={'redirect_uri': redirect_uri})
            )
        )
        return redirect(auth_url)
    return redirect('login')


@require_GET
def aad_redirect(request, redirect_uri):
    ms_identity_web.process_auth_redirect(
        request,
        redirect_uri=request.build_absolute_uri(request.path),
    )
    return redirect(f'/{redirect_uri}')


@require_GET
def sign_out(request, redirect_uri):
    if ENABLE_SSO:
        sign_out_url = ms_identity_web.get_sign_out_url(
            redirect_uri=request.build_absolute_uri(
                reverse('drfmsal_postsignout', kwargs={
                    'redirect_uri': redirect_uri})
            )
        )
        return redirect(sign_out_url)
    return redirect('logout')


@require_GET
def post_sign_out(request, redirect_uri):
    ms_identity_web.remove_user(request)
    return redirect(f'/{redirect_uri}')
