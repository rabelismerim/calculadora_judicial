from rest_framework.authentication import TokenAuthentication
from rest_framework.renderers import JSONRenderer

from config.settings import ENABLE_TOKEN
from utils import get_user_model

User = get_user_model()


class APIRendererInterceptor(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and 'request' in renderer_context:
            request = renderer_context['request']

            if isinstance(request.successful_authenticator, TokenAuthentication) or not hasattr(request._request,
                                                                                                'identity_context_data'):
                is_authenticated = request.user.is_authenticated
                data = {
                    'data': data,
                    'application_response': True,
                    'accept_token': True,
                    'profile': {
                        'authorized': is_authenticated,
                        'is_active': request.user.is_active,
                        'is_staff': request.user.is_staff,
                        'authenticated': is_authenticated,
                        'user_fullname': request.user.get_full_name if is_authenticated else 'anonymous',
                        'user_picture': None,
                    }
                }
            else:
                identity_context_data = request._request.identity_context_data
                authorized = request.user.is_authenticated
                is_active = request.user.is_active

                if ENABLE_TOKEN:
                    authenticated = identity_context_data.authenticated or request.user.is_authenticated
                else:
                    authenticated = identity_context_data.authenticated

                full_name = identity_context_data.username
                if request.user.is_authenticated and hasattr(request.user, 'full_name'):
                    full_name = request.user.full_name
                if authenticated and not is_active:
                    user = User.objects.filter(email=identity_context_data.usermail).first()
                    if user:
                        is_active = user.is_active
                data = {
                    'data': data,
                    'application_response': True,
                    'accept_token': False,
                    'profile': {
                        'authorized': authorized,
                        'is_active': is_active,
                        'is_staff': request.user.is_staff,
                        'authenticated': authenticated,
                        'user_fullname': full_name,
                        'user_picture': identity_context_data.userpicture,
                    }
                }

        return super().render(data, accepted_media_type, renderer_context)
