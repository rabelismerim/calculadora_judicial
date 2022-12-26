from rest_framework.renderers import JSONRenderer


class APIRendererInterceptor(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and 'request' in renderer_context:
            request = renderer_context['request']
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