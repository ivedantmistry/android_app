from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    def __init__(self, user_id=None, email=None, user_type=None, **kwargs):
        super().__init__(**kwargs)
        self['user_id'] = user_id
        self['email'] = email
        self['user_type'] = user_type
