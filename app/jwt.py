# import jwt
# from django.conf import settings

# def jwt_encode(payload):
# 	payload['iss'] = 'TempNet'
# 	payload['aud'] = 'TempNet-clients'
# 	try:
# 		return jwt.encode(
# 			payload,
# 			settings.JWT_PRIVATE_KEY,
# 			algorithm='RS256',
# 		)
# 	except Exception as e:
# 		print(f"JWT encode error: {str(e)}")
# 		return None


# def jwt_decode(jwt_token):
# 	try:
# 		return jwt.decode(
# 			jwt_token,
# 			settings.JWT_PUBLIC_KEY,
# 			algorithms=['RS256'],
# 			issuer='TempNet',
# 			audience='TempNet-clients',
# 		)
# 	except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidIssuerError, jwt.InvalidAudienceError) as e:
# 		print(f"JWT decode error: {str(e)}")
# 		return None
import jwt
import uuid
import datetime
from django.conf import settings
from django.utils import timezone
from .models import RefreshToken

def jwt_encode(payload, exp_delta):
    now = timezone.now()
    payload = {
        **payload,
        'iss': 'TempNet',
        'aud': 'TempNet-clients',
        'iat': int(now.timestamp()),
        'exp': int((now + exp_delta).timestamp()),
    }
    try:
        return jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm='RS256')
    except Exception as e:
        print(f"JWT encode error: {str(e)}")
        return None

def create_access_token(user):
    return jwt_encode(
        {'uid': user.id, 'un': user.username, 'type': 'access'},
        datetime.timedelta(hours=1),
    )

def create_refresh_token(user):
    rt = RefreshToken.objects.create(
        user=user,
        expires_at=timezone.now() + datetime.timedelta(hours=5),
    )
    token = jwt_encode(
        {'uid': user.id, 'jti': str(rt.jti), 'type': 'refresh'},
        datetime.timedelta(minutes=5),
    )
    return token

def jwt_decode(jwt_token):
    try:
        return jwt.decode(
            jwt_token,
            settings.JWT_PUBLIC_KEY,
            algorithms=['RS256'],
            issuer='TempNet',
            audience='TempNet-clients',
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidIssuerError, jwt.InvalidAudienceError) as e:
        print(f"JWT decode error: {str(e)}")
        return None