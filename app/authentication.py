from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

from .jwt import jwt_decode


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()
        payload = jwt_decode(token)
        if payload is None:
            raise AuthenticationFailed('Invalid or expired token')

        # refresh tokens must never be accepted as access tokens
        if payload.get('type') != 'access':
            raise AuthenticationFailed('Invalid token type')

        try:
            user = User.objects.get(id=payload.get('uid'), is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, payload)

    def authenticate_header(self, request):
        # makes DRF answer 401 (instead of 403) so the frontend can refresh the token
        return 'Bearer'
