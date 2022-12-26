 
from django.conf import settings

from .adapter import DjangoContextAdapter
from .errors import NotAuthenticatedError


ms_identity_web = settings.DRFMSAL_IDENTITY_WEB

class MsalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ms_identity_web = ms_identity_web
    
    def process_exception(self, request, exception):
        if isinstance(exception, NotAuthenticatedError):
            raise exception                
        return None

    def __call__(self, request):
        django_context_adapter = DjangoContextAdapter(request)
        self.ms_identity_web.set_adapter(django_context_adapter)

        django_context_adapter._on_request_init()
        
        response = self.get_response(request)

        django_context_adapter._on_request_end()

        return response
        