from msal import ConfidentialClientApplication

from base64 import b64encode
from functools import wraps
from logging import Logger
from requests import get
from uuid import uuid4

from .adapter import DjangoContextAdapter
from .constants import *
from .errors import *


# TODO:
#  ##### IMPORTANT #####
# features:
# - do configurations work on multi-threaded flask environment? if not, attach them to current_app. configurations aren't stateful so this may be a moot point?
# - edit profile interaction required error on edit profile if no token_cache or expired?
# - pw reset should use login hint/no interaction?
# - decorator for filter by security groups
# - decorator for app roles RBAC
# - auth failure handler to handle un-auth access?
# - implement more client_type options (single and multi tenant)
# - define django adapter: factor common adapter methods to a parent class that flask and django adapters inherit
#
# code quality:
# - more try catch blocks around sensitive failure-prone methods for gracefule error-handling
# 
# ###### LOWER PRIORITY ##########
# - remove any print statements
# - replace is comparators with == ?
# - cleanup / refactor constants file

def build_add_config():
    from types import SimpleNamespace
    from django.conf import settings

    def dict_to_namespace(d):
        ns = SimpleNamespace()
        for k, v in d.items():
            setattr(ns, k, dict_to_namespace(v) if isinstance(v, dict) else v)
        return ns

    def sanity_check_configs(parsed_config):
        required = ['id_web_configs', 'graph_url', 'client', 'auth_request']
        for req in required: assert hasattr(parsed_config, req)

        required = ['client_id', 'client_credential', 'authority']
        for req in required: assert str(getattr(parsed_config.client, req, '')), f"'{req}' must be non-empty string"

        required = ['scopes', 'response_type']
        for req in required: assert hasattr(parsed_config.auth_request, req)

    parsed_config = dict_to_namespace(settings.DRFMSAL_CONFIG)
    sanity_check_configs(parsed_config)

    return parsed_config


def require_context_adapter(f):
    @wraps(f)
    def assert_adapter(self, *args, **kwargs):
        if not isinstance(self._adapter, DjangoContextAdapter):
            if self._logger:
                self._logger.info(
                    f"{self.__class__.__name__}.{f.__name__}: invalid adapter or no request context, aborting")
            else:
                logging.info(f"{self.__class__.__name__}.{f.__name__}: invalid adapter or no request context, aborting")
        return f(self, *args, **kwargs)

    return assert_adapter


class IdentityWebPython(object):

    def __init__(self, adapter=None, logger=None, resolution='240x240'):
        self._logger = logger or Logger('IdentityWebPython')
        self._adapter = None
        self.aad_config = build_add_config()
        self.resolution = resolution
        if adapter is not None:
            self.set_adapter(adapter)

    @property
    @require_context_adapter
    def id_data(self):
        return self._adapter.identity_context_data

    # TODO: make the call from the adapter to this and reverse the config process?
    def set_adapter(self, adapter):
        self._adapter = adapter
        adapter.attach_identity_web_util(self)

    def set_logger(self, logger):
        self._logger = logger

    def _client_factory(self, token_cache=None, **msal_client_kwargs):
        client_config = self.aad_config.client.__dict__.copy()  # need to make a copy since contents must be mutated
        client_config['authority'] = f'{self.aad_config.client.authority}'
        if token_cache:
            client_config['token_cache'] = token_cache
        client_config.update(**msal_client_kwargs)

        return ConfidentialClientApplication(**client_config)

    @require_context_adapter
    def get_auth_url(self, redirect_uri, **msal_auth_url_kwargs):
        """ Gets the auth URL that the user must be redirected to."""
        auth_req_options = self.aad_config.auth_request.__dict__.copy()
        auth_req_options.update(**msal_auth_url_kwargs)
        auth_req_options['redirect_uri'] = redirect_uri
        self._generate_and_append_state_to_context_and_request(auth_req_options)

        if self.id_data.authenticated:
            auth_req_options['login_hint'] = self.id_data._id_token_claims.get('preferred_username', None)

        return self._client_factory().get_authorization_request_url(**auth_req_options)

    @require_context_adapter
    def process_auth_redirect(self, request, redirect_uri, response_type=None):
        req_params = self._adapter.get_request_params_as_dict()  # grab the incoming request params
        try:
            # CSRF protection: make sure to check that state matches the one placed in the session in the previous step.
            # This check ensures this app + this same user session made the /authorize request that resulted in this redirect
            # This should always be the first thing verified on redirect.
            self._verify_state(req_params)

            self._logger.info("process_auth_redirect: state matches. continuing.")
            self._parse_redirect_errors(req_params)
            self._logger.info("process_auth_redirect: no errors found in request params. continuing.")

            # get the response_type that was requested, and extract the payload:
            resp_type = response_type or self.aad_config.auth_request.response_type or str(ResponseType.CODE)
            payload = self._extract_auth_response_payload(req_params, resp_type)
            cache = self._adapter.identity_context_data.token_cache

            if resp_type == str(
                    ResponseType.CODE):  # code request is default for msal-python if there is no response type specified
                # we should have a code. Now we must exchange the code for tokens.
                result = self._x_change_auth_code_for_token(payload, cache, redirect_uri)
            else:
                raise NotImplementedError(f"response_type {resp_type} is not yet implemented by ms_identity_web_python")
            self._process_result(request, result, cache)
            # self._verify_nonce() # one of the last steps TODO - is this required? msal python takes care of it?
        except AuthSecurityError as ase:
            self.remove_user(request)
            self._logger.error(f"process_auth_redirect: security violation {ase.args}")
            raise ase
        except OtherAuthError as oae:
            self.remove_user(request)
            self._logger.error(f"process_auth_redirect: other auth error {oae.args}")
            raise oae
        except TokenExchangeError as ter:
            self.remove_user(request)
            self._logger.error(f"process_auth_redirect: token xchange {ter.args}")
            raise ter
        except BaseException as other:
            self.remove_user(request)
            self._logger.error(f"process_auth_redirect: unknown error{other.args}")
            raise other

        # TODO: GET /auth/redirect?error=interaction_required&error_description=AADB2C90077%3a+User+does+not+have+an+existing+session+and+request+prompt+parameter+has+a+value+of+%27None%27.
        # self._logger.info("process_auth_redirect: exiting auth code method. redirecting... ")
        # return self._adapter.redirect_to_absolute_url(afterwards_go_to_url)

    @require_context_adapter
    def _x_change_auth_code_for_token(self, code, token_cache=None, redirect_uri=None):
        # use the same policy that got us here: depending on /authorize request initiation
        id_context = self._adapter.identity_context_data
        client = self._client_factory(token_cache=token_cache)
        return client.acquire_token_by_authorization_code(code,
                                                          self.aad_config.auth_request.scopes,
                                                          redirect_uri,
                                                          id_context.nonce)

    @require_context_adapter
    def acquire_token_silently(self, request, scopes=None, account=None, authority=None, token_cache=None, **kwargs):
        # the params take precedence over settings file.
        id_data = self.id_data
        token_cache = token_cache or id_data.token_cache
        client = self._client_factory(token_cache=token_cache)

        silent_opts = {**kwargs}
        silent_opts['scopes'] = scopes or self.aad_config.auth_request.scopes
        silent_opts['account'] = account or client.get_accounts()[0]

        result = client.acquire_token_silent_with_error(**silent_opts)

        self._process_result(request, result, token_cache)

    @require_context_adapter
    def _process_result(self, request, result, token_cache):
        if "error" not in result:
            self._logger.debug("process result: successful token response result!")
            # now we will place the token(s) and auth status into the context for later use:
            # self._logger.debug(json.dumps(result, indent=4, sort_keys=True))
            id_context = self._adapter.identity_context_data
            id_context.authenticated = True
            if 'id_token_claims' in result:
                id_context._id_token_claims = result[
                    'id_token_claims']  # TODO: if this is to stay in ctxt, use proper getter/setter
                username = id_context._id_token_claims.get('name', 'anonymous')
                if ', ' in username:
                    username_temp = username.split(', ')
                    username = f'{username_temp[1].split()[0]} {username_temp[0]}'
                id_context.username = username

                id_context.usermail = id_context._id_token_claims.get('preferred_username', None)
            if 'access_token' in result:
                id_context._access_token = result['access_token']
                id_context.userpicture = self._get_userpicture(result['access_token'])
            id_context.has_changed = True  # TODO: update id_context to automatically do this when _id_token and accesstoken is assigned!!!!
            id_context.token_cache = token_cache

            self._handle_django_login(request)

        else:
            raise TokenExchangeError("_process_result: auth failed: token request resulted in error\n"
                                     f"{result['error']}: {result.get('error_description', None)}")

    def _get_userpicture(self, access_token):
        graph_url = f'{self.aad_config.graph_url.rstrip("/")}/me/photos/{self.resolution}/$value'
        auth_z = f'Bearer {access_token}'
        picture_response = get(graph_url, headers={'Authorization': auth_z}, stream=True, verify=False)
        picture = picture_response.raw.read() or picture_response.content or ''
        try:
            return b64encode(picture).decode('ascii') if picture_response.ok and picture else None
        except (KeyError, ValueError, TypeError):
            pass

    def _parse_redirect_errors(self, req_params):
        # TODO implement all errors which affect program behaviour
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow
        if str(AADErrorResponse.ERROR_CODE_PARAM_KEY) in req_params:
            # TODO: add more error types
            raise OtherAuthError("Unknown error while parsing redirect")

    def _extract_auth_response_payload(self, req_params, expected_response_type):
        if expected_response_type == str(ResponseType.CODE):
            # if no response type in config, default response type of 'code' will have been assumed.
            return req_params.get(str(ResponseType.CODE), None)
        else:
            raise NotImplementedError("Only 'code' response is currently supported by identity utils")

    @require_context_adapter
    def get_sign_out_url(self, redirect_uri=None):
        sign_out_url = f'{self.aad_config.client.authority}{SignOut.ENDPOINT.value}'
        if redirect_uri:
            sign_out_url = f'{sign_out_url}?{SignOut.REDIRECT_PARAM_KEY.value}={redirect_uri}'
        return sign_out_url

    @require_context_adapter
    def remove_user(self, request):  # TODO: complete this so it doesn't just clear the session but removes user
        self._handle_django_logout(request)
        self._adapter.clear_session()
        # TODO e.g. if active username in id_context_'s username is not anonymous, remove it
        # remove id token
        # remote AT
        # remove token_cache
        # TODO: set auth_state_changed flag here

    @require_context_adapter
    def _generate_and_append_state_to_context_and_request(self, req_param_dict):
        state = str(uuid4())
        req_param_dict[RequestParameter.STATE.value] = state
        self._adapter.identity_context_data.state = state
        return state

    @require_context_adapter
    def _verify_state(self, req_params):
        state = req_params.get('state', None)
        session_state = self._adapter.identity_context_data.state
        # don't allow re-use of state
        self._adapter.identity_context_data.state = None
        # reject states that don't match
        if state is None or session_state != state:
            raise AuthSecurityError("Failed to match request state with session state")

    @require_context_adapter
    def _generate_and_append_nonce_to_context_and_request(self, req_param_dict):
        nonce = str(uuid4())
        req_param_dict[RequestParameter.NONCE.value] = nonce
        self._adapter.identity_context_data.nonce = nonce
        return nonce

    @require_context_adapter
    def _verify_nonce(self, req_params):
        nonce = req_params.get('nonce', None)
        session_nonce = self._adapter.identity_context_data.nonce
        # don't allow re-use of nonce
        self._adapter.identity_context_data.nonce = None
        # reject nonces that don't match
        if nonce is None or session_nonce != nonce:
            raise AuthSecurityError("Failed to match ID token nonce with session nonce")

    # TODO: enforce ID token expiry.
    # @decorator to ensure the user is authenticated
    # wrap this around your route    
    def login_required(self, f):
        @wraps(f)
        def assert_login(*args, **kwargs):
            if not self._adapter.identity_context_data.authenticated:
                raise NotAuthenticatedError
            # TODO: check if ID token is expired
            # if it is, take user to get re-authenticated.
            # TODO: upon returning from re-auth, user should get back to
            # where they were trying to go.
            return f(*args, **kwargs)

        return assert_login

    # Django iterface - DigitalLAB: Ewerson Silva
    def _handle_django_login(self, request):
        if not request.user.is_authenticated:
            id_data = request.identity_context_data
            if id_data.usermail is not None:
                from django.apps import apps
                from django.conf import settings

                User = apps.get_model(settings.AUTH_USER_MODEL)
                email = str(id_data.usermail).lower()
                user_view = User.objects.filter(email=email)

                if not user_view and id_data.usermail is not None:
                    user = User()
                    user.email = email
                    user.username = email.split('@')[0]
                    user.first_name = id_data.username.split()[0]
                    user.last_name = id_data.username.split()[-1]
                    user.is_active = False
                    user.userpicture = id_data.userpicture
                    user.is_staff = False
                    user.save()
                    user.create_photo()
                django_user = user_view.filter(is_active=True).first()

                for item in user_view:
                    if item.userpicture != id_data.userpicture or not item.user_img:
                        item.userpicture = id_data.userpicture
                        item.save()
                        item.create_photo(force=True)
                if django_user:
                    from django.contrib.auth import login
                    login(request, django_user)

    def _handle_django_logout(self, request):
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
