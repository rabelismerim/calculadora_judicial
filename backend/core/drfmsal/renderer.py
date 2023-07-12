from rest_framework.renderers import JSONRenderer

from config.settings import ENABLE_SSO
from utils import get_user_model

User = get_user_model()


class APIRendererInterceptor(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and 'request' in renderer_context:
            request = renderer_context['request']
            if ENABLE_SSO is False:
                is_authenticated = request.user.is_authenticated
                data = {
                    'data': data,
                    'dttdjud': True,
                    'accept_token': True,
                    'profile': {
                        'authorized': is_authenticated,
                        'is_active': request.user.is_active,
                        'authenticated': is_authenticated,
                        'user_fullname': request.user.get_full_name if is_authenticated else 'anonymous',
                        'user_picture': None,
                    }
                }
            else:
                identity_context_data = request._request.identity_context_data
                authorized = request.user.is_authenticated
                is_active = request.user.is_active
                authenticated = identity_context_data.authenticated

                if authenticated and not is_active:
                    user = User.objects.filter(email=identity_context_data.usermail).first()
                    if user:
                        is_active = user.is_active
                data = {
                    'data': data,
                    'dttdjud': True,
                    'accept_token': False,
                    'profile': {
                        'authorized':authorized,
                        'is_active': is_active,
                        'authenticated': authenticated,
                        'user_fullname': identity_context_data.username,
                        'user_picture': identity_context_data.userpicture,
                    }
                }
        return super().render(data, accepted_media_type, renderer_context)
