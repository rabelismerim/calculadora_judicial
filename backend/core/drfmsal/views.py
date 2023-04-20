from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from config.settings import ENABLE_SSO
from core.abstract.views import AbstractViewApi, CustomSchema as AutoSchema
from core.drfmsal.schemas import SignStatusSerializer

from core.dttuser.models import User
from core.dttuser.schemas import UserDttMFASchema
from utils import doc, _

ms_identity_web = settings.DRFMSAL_IDENTITY_WEB


class SignStatusApi(AbstractViewApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['get']
    query_params = []
    docs = {
        'init': _("""Sign Status shows details of the user who made the request, such as `authorized`, `authenticated`,
         `profile` and others.
        """)
    }
    serializer_class = SignStatusSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    @doc(_("""This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """))
    def get(self, request, *args, **kwargs):
        if ENABLE_SSO and ms_identity_web.id_data:
            user_view = User.objects.filter(
                email=ms_identity_web.id_data.usermail)
            if ms_identity_web.id_data.usermail is not None:
                if user_view.count() == 0:
                    serializer = UserDttMFASchema(data=ms_identity_web.id_data)
                    serializer.is_valid(raise_exception=True)
                    new_user = serializer.data
                    User.objects.create_user(**new_user)
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
            redirect_uri=request.build_absolute_uri(reverse('drfmsal_redirect', kwargs={'redirect_uri': redirect_uri})))
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
            redirect_uri=request.build_absolute_uri(reverse('drfmsal_postsignout',
                                                            kwargs={'redirect_uri': redirect_uri})))
        return redirect(sign_out_url)
    return redirect('logout')


@require_GET
def post_sign_out(request, redirect_uri):
    ms_identity_web.remove_user(request)
    return redirect(f'/{redirect_uri}')
