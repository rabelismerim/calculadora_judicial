from msal import SerializableTokenCache

# TODO: make this a @dataclass ?

class IdentityContextData(object):
    SESSION_KEY='identity_context_data' #TODO: make configurable

    def __init__(self):
        self.clear()
        self.has_changed = False

    def clear(self):
        self._authenticated = False
        self._username = "anonymous"
        self._usermail = None
        self._userpicture = None
        self._token_cache = None
        self._nonce = None
        self._state = None
        self._id_token_claims = {} # does this belong here? yes, Token/claims customization. TODO: if it does, add getter/setter, # ID tokens aren't cached so store this here? 
        self._access_token = None
        self._post_sign_in_url = None
        self.has_changed = True

    @property
    def authenticated(self):
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value):
        self._authenticated = value
        self.has_changed = True

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.has_changed = True
    
    @property
    def usermail(self):
        return self._usermail

    @usermail.setter
    def usermail(self, value):
        self._usermail = value
        self.has_changed = True

    @property
    def userpicture(self):
        return self._userpicture

    @userpicture.setter
    def userpicture(self, value):
        self._userpicture = value
        self.has_changed = True

    @property
    def token_cache(self):
        cache = SerializableTokenCache()
        if self._token_cache:
            cache.deserialize(self._token_cache)
        return cache

    @token_cache.setter
    def token_cache(self, value):
        if value.has_state_changed:
            self._token_cache = value.serialize()
            self.has_changed = True

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.has_changed = True

    @property
    def nonce(self):
        return self._nonce

    @nonce.setter
    def nonce(self, value):
        self._nonce = value
        self.has_changed = True

    @property
    def post_sign_in_url(self):
        return self._post_sign_in_url

    @post_sign_in_url.setter
    def post_sign_in_url(self, value):
        self._post_sign_in_url = value
        self.has_changed = True
