from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.urls.exceptions import Resolver404, NoReverseMatch
from django.utils.encoding import iri_to_uri
from django.utils.http import url_has_allowed_host_and_scheme
from drf_yasg import openapi
from rest_framework import permissions

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from config.settings import ENABLE_SSO, DRFMSAL_IDENTITY_WEB, ENABLE_TOKEN
from core.abstract.views import AbstractViewApi
from core.drfmsal.schemas import SignStatusSerializer, MFASerializer

from core.users.models import User
from utils import doc, _

ms_identity_web = DRFMSAL_IDENTITY_WEB


class ClearCacheApi(AbstractViewApi):
    """This class represents the HTTP methods for User calculadora. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['get']

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
    """This class represents the HTTP methods for User calculadora. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['get']

    docs = {
        'init': _("""Sign Status shows details of the user who made the request, such as `authorized`, `authenticated`,
         `profile` and others.
        """)
    }
    serializer_class = SignStatusSerializer
    permission_classes = [AllowAny]
    if not ENABLE_TOKEN:
        authentication_classes = [SessionAuthentication]
    else:
        authentication_classes = [SessionAuthentication, TokenAuthentication]
    allow_cache = False
    operation_id_base = 'Get Sign Status'

    @doc(_("""This method returns a JSON response that contains the user details as per authenticated user.
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """))
    def get(self, request, *args, **kwargs):
        if ENABLE_SSO and ms_identity_web.id_data:
            email = str(ms_identity_web.id_data.usermail).lower()
            user_view = User.objects.filter(email=email)
            if ms_identity_web.id_data.usermail is not None:
                if user_view.count() == 0:
                    user = User()
                    user.email = email
                    user.username = email.split('@')[0]
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
                        if item.userpicture != ms_identity_web.id_data.userpicture or not item.user_img:
                            item.userpicture = ms_identity_web.id_data.userpicture
                            item.save()
                            item.create_photo(force=True)

        return Response()


@doc(_("""View for signing in a user.

    This view is intended to be used in a regular web browser and is not designed to be accessed directly as an API.
    It serves as a documentation reference within the API.

    The GET request to this view handles the sign-in process for a user. If Single Sign-On (SSO) is enabled,
    it redirects the user to the authentication page. Otherwise, it redirects the user to the login page.

    Methods:
    - get: Handles the GET request for signing in a user.
    """))
class SignInView(AbstractViewApi):
    http_method_names = ['get']
    serializer_class = MFASerializer
    permission_classes = [AllowAny]
    redirection_response = openapi.Response('This endpoint is redirecting user to the: `http:example.com`')
    responses = {302: {'url': '/login', 'message': 'Redirecting to authentication page'}}

    @doc(_("""Handle GET request for signing in a user.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A redirect response to the authentication page or login page.
        """))
    def get(self, request, *args, **kwargs):
        if ENABLE_SSO:
            redirect_uri = kwargs.get('redirect_uri')
            auth_url = ms_identity_web.get_auth_url(
                redirect_uri=request.build_absolute_uri(
                    reverse('drfmsal_redirect', kwargs={'redirect_uri': redirect_uri})))
            return redirect(auth_url)
        return redirect('login')


class CustomRedirectURLMixin:
    next_page = None
    redirect_field_name = 'redirect_uri'
    success_url_allowed_hosts = set()

    def get_success_url(self):
        return self.get_redirect_url() or self.get_default_redirect_url()

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.resolver_match.kwargs.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, self.request.POST.get(self.redirect_field_name)),
        )

        if not redirect_to.startswith('http') and not redirect_to.startswith('/'):
            redirect_to = iri_to_uri(f'/{redirect_to}')
        else:
            redirect_to = iri_to_uri(redirect_to)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )

        return redirect_to if url_is_safe else None

    def get(self, request, *args, **kwargs):
        try:
            next_url = self.get_success_url()
            return redirect(resolve_url(next_url))
        except (Resolver404, NoReverseMatch):
            return HttpResponseBadRequest("Invalid redirect_uri format")

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        raise ImproperlyConfigured("No URL to redirect to. Provide a next_page.")


@doc("""View for handling Azure Active Directory (AAD) redirects.

    This view is intended to be used in a regular web browser and is not designed to be accessed directly as an API.
    It serves as a documentation reference within the API.

    The GET request to this view handles the redirect process after authentication with Azure Active Directory (AAD).
    It processes the authentication redirect and redirects the user to the specified redirect URI.

    Attributes:
    - http_method_names: The allowed HTTP methods for this view.
    - serializer_class: The serializer class used for validating and deserializing input data.
    - permission_classes: The permission classes applied to this view.
    - responses: The custom responses for this view.

    Methods:
    - get: Handles the GET request for handling AAD redirects.
    """)
class AADRedirectView(CustomRedirectURLMixin, AbstractViewApi):
    http_method_names = ['get']
    serializer_class = MFASerializer
    permission_classes = [AllowAny]
    responses = {302: {'url': '/redirect_uri', 'message': _('Redirecting to redirect_uri')}}
    operation_id_base = 'AADRedirect'

    @doc(_("""Handle GET request for handling AAD redirects.

        Returns:
        - A redirect response to the specified redirect URI.
        """))
    def get(self, request, *args, **kwargs):
        ms_identity_web.process_auth_redirect(
            request,
            redirect_uri=request.build_absolute_uri(request.path),
        )
        return super().get(request, *args, **kwargs)


def allowed_domain(redirect_uri):
    """Define and validate a whitelist of allowed domains"""
    domain = ms_identity_web.aad_config.client.authority
    parsed_domain = urlparse(domain).netloc
    redirect_domain = urlparse(redirect_uri).netloc
    return redirect_domain in parsed_domain


@doc(_("""View for signing out a user.

    This view is intended to be used in a regular web browser and is not designed to be accessed directly as an API.
    It serves as a documentation reference within the API.

    The GET request to this view handles the sign-out process for a user. If Single Sign-On (SSO) is enabled,
    it redirects the user to the sign-out page. Otherwise, it redirects the user to the logout page.

    Methods:
    - get: Handles the GET request for signing out a user.
    """))
class SignOutView(AbstractViewApi):
    http_method_names = ['get']
    serializer_class = MFASerializer
    permission_classes = [AllowAny]
    responses = {302: {'url': '/logout', 'message': _('Redirecting to logout page')}}
    operation_id_base = 'SignOut'

    @doc(_("""Handle GET request for signing out a user.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A redirect response to the sign-out page or logout page.
        """))
    def get(self, request, *args, **kwargs):
        redirect_uri = kwargs.get('redirect_uri')

        if ENABLE_SSO:
            sign_out_url = ms_identity_web.get_sign_out_url(
                redirect_uri=request.build_absolute_uri(reverse('drfmsal_postsignout',
                                                                kwargs={'redirect_uri': redirect_uri})))

            if allowed_domain(sign_out_url):
                return redirect(sign_out_url)
        return redirect('logout')


@doc(_("""View for handling post-sign-out actions.

    This view is intended to be used in a regular web browser and is not designed to be accessed directly as an API.
    It serves as a documentation reference within the API.

    The GET request to this view handles the post-sign-out process for a user. It removes the user's session and
    redirects the user to the specified redirect URI.

    Methods:
    - get: Handles the GET request for post-sign-out actions.
    """))
class PostSignOutView(CustomRedirectURLMixin, AbstractViewApi):
    http_method_names = ['get']
    serializer_class = MFASerializer
    permission_classes = [AllowAny]
    responses = {302: {'url': '/redirect_uri', 'message': _('Redirecting to redirect_uri')}}
    operation_id_base = 'PostSignOut'

    @doc(_("""Handle GET request for post-sign-out actions.

        Parameters:
        - request: The HTTP request object.
        - args: Additional positional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - A redirect response to the specified redirect URI.
        """))
    def get(self, request, *args, **kwargs):
        ms_identity_web.remove_user(request)
        return super().get(request, *args, **kwargs)
