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

        try:
            user = User.objects.get(id=payload.get('uid'))
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return (user, payload)