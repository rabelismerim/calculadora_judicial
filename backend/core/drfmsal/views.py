import base64
import hashlib
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET
from rest_framework import permissions

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


class ClearCacheApi(AbstractViewApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['get']
    query_params = []
    docs = {
        'init': _("""This view forces the platform to clear caches so that any get methods are reloaded. The platform 
        has cache control in case there is any change, but if this control fails, this view can be used )""")
    }
    serializer_class = SignStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    allow_cache = False
    operation_id_base = 'Get Clear Cache'

    @doc(_("""This method returns a Default response"""))
    def get(self, request, *args, **kwargs):
        self.delete_cache_from_user()
        return Response()


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
    allow_cache = False
    operation_id_base = 'Get Sign Status'

    @doc(_("""This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """))
    def get(self, request, *args, **kwargs):
        if ENABLE_SSO and ms_identity_web.id_data:
            user_view = User.objects.filter(
                email=ms_identity_web.id_data.usermail)
            if ms_identity_web.id_data.usermail is not None:
                if user_view.count() == 0:
                    user = User()
                    user.email = ms_identity_web.id_data.usermail
                    user.username = ms_identity_web.id_data.username.replace(' ', '_')
                    user.first_name = ms_identity_web.id_data.username.split()[0]
                    user.last_name = ms_identity_web.id_data.username.split(
                    )[len(request.identity_context_data.username.split()) - 1]
                    user.is_active = False
                    user.userpicture = ms_identity_web.id_data.userpicture
                    user.is_staff = False
                    user.save()
                elif len(user_view) > 0:
                    for item in user_view:
                        # TODO salvar foto recebida em base64 para img Field e passar a url para o front
                        if item.userpicture != ms_identity_web.id_data.userpicture:
                            item.userpicture = ms_identity_web.id_data.userpicture
                            item.save()

                            data = ContentFile(base64.b64decode(ms_identity_web.id_data.userpicture))
                            file_name = f"{uuid.uuid4()}.jpeg"
                            item.user_img.save(file_name, data, save=True)  # image is User's model field

                            try:
                                data = ContentFile(base64.b64decode(item.userpicture))
                                image_data = base64.b64decode(item.userpicture)
                                file_hash = hashlib.md5(image_data).hexdigest()
                                file_name = f"{file_hash}.jpeg"
                                if item.user_img and str(item.user_img.name) in file_name is False:
                                    item.user_img.save(file_name, data, save=True)  # image is User's model field
                                    item.save()
                            except Exception as e:
                                print(e, 'err save img in base64')
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
