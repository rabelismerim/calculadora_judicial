from rest_framework.renderers import JSONRenderer

from config.settings import BRANCH_LOCAL, IS_LOCALHOST


class APIRendererInterceptor(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and 'request' in renderer_context:
            request = renderer_context['request']
            if IS_LOCALHOST or BRANCH_LOCAL:
                is_authenticated = request.user.is_authenticated
                data = {
                    'data': data,
                    'dttdare': True,
                    'profile': {
                        'authorized': is_authenticated,
                        'authenticated': is_authenticated,
                        'user_fullname': request.user.get_full_name if is_authenticated else 'anonymous',
                        'user_picture': None,
                    }
                }
            else:
                identity_context_data = request._request.identity_context_data
                data = {
                    'data': data,
                    'dttdare': True,
                    'profile': {
                        'authorized': request.user.is_authenticated,
                        'authenticated': identity_context_data.authenticated,
                        'user_fullname': identity_context_data.username,
                        'user_picture': identity_context_data.userpicture,
                    }
                }
        return super().render(data, accepted_media_type, renderer_context)
