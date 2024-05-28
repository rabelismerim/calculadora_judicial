import logging
from .context import IdentityContextData


class DjangoContextAdapter:
    """Context Adapter to enable IdentityWebPython to work within the Django environment"""
    def __init__(self, request):
        # TODO: remove the following and add a middleware loaded before this one for global request/session context?
        self.request = request
        self._session = request.session
        self.logger = logging.getLogger('MsalMiddleWareLogger')

    @property
    def identity_context_data(self):
        # TODO: make the key name configurable
        self.logger.debug("Getting identity_context from request/session")
        identity_context_data = getattr(self.request, IdentityContextData.SESSION_KEY, None)
        if not identity_context_data:

            identity_context_data = self._deserialize_identity_context_data_from_session()
            setattr(self.request, IdentityContextData.SESSION_KEY, identity_context_data)
        return identity_context_data

    def _on_request_init(self):
        try:
            idx = self.identity_context_data # initialize it so it is available to request context
        except Exception as ex:
            self.logger.error(f'MsalMiddleware failed @ _on_request_init\n{ex}')

    # this is for saving any changes to the identity_context_data
    def _on_request_end(self):
        try:
            if getattr(self.request, IdentityContextData.SESSION_KEY, None):
                self._serialize_identity_context_data_to_session()
        except Exception as ex:
            self.logger.error(f'MsalMiddleware failed @ _on_request_ended\n{ex}')

    # TODO: order is reveresed? create id web first, then attach django adapter to it!?
    def attach_identity_web_util(self, identity_web):
        """attach the identity web instance somewhere so it is accessible everywhere.
        e.g., ms_identity_web = current_app.config.get("ms_identity_web")\n
        Also attaches the application logger."""
        aad_config = identity_web.aad_config
        config_key = aad_config.id_web_configs
        setattr(self.request, config_key, aad_config)
        

    @property
    def session(self):
        return self._session

    # TODO: only clear IdWebPy vars
    def clear_session(self):
        """this function clears the session and refreshes context. TODO: only clear IdWebPy vars"""
        # TODO: clear ONLY msidweb session stuff
        self.session.flush()
    
    def get_value_from_session(self, key, default=None):
        return self.session.get(key, default)

    def get_request_params_as_dict(self):
        try:
            if self.request.method == "GET":
                return self.request.GET.dict()
            elif self.request.method == "POST" :
                return self.request.POST.dict()
            else:
                raise ValueError("Django request must be POST or GET")
        except Exception as e:
            logging.error(e, exc_info=True)
            if self.logger is not None:
                self.logger.warning("Failed to get param dict, substituting empty dict instead")
            return dict()        

    # does this need to be public method?
    def _deserialize_identity_context_data_from_session(self):
        blank_id_context_data = IdentityContextData()
        try:
            id_context_from_session = self.session.get(IdentityContextData.SESSION_KEY, dict())
            blank_id_context_data.__dict__.update(id_context_from_session)
        except Exception as exception:
            self.logger.warning(f"failed to deserialize identity context from session: creating empty one\n{exception}")
        return blank_id_context_data

    # does this need to be public method?
    def _serialize_identity_context_data_to_session(self):
        try:
            identity_context = self.identity_context_data
            if identity_context.has_changed:
                identity_context.has_changed = False
                identity_context = identity_context.__dict__
                self.session[IdentityContextData.SESSION_KEY] = identity_context
        except Exception as exception:
            self.logger.error(f"failed to serialize identity context to session.\n{exception}")
