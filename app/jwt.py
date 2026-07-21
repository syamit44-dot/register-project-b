import jwt
from django.conf import settings

def jwt_encode(payload):
	payload['iss'] = 'TempNet'
	payload['aud'] = 'TempNet-clients'
	try:
		return jwt.encode(
			payload,
			settings.JWT_PRIVATE_KEY,
			algorithm='RS256',
		)
	except Exception as e:
		print(f"JWT encode error: {str(e)}")
		return None


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