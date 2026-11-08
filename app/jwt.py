import ipaddress
import time
import datetime
import jwt
from urllib.parse import urlparse
from django.conf import settings
from django.http.request import split_domain_port
from django.utils import timezone
from .models import RefreshToken

REFRESH_COOKIE_NAME = 'refresh_token'
LOCAL_HOSTS = {'localhost', '127.0.0.1'}
# second-level labels used under 2-letter ccTLDs (co.th, ac.th, com.au, ...)
SECOND_LEVEL_LABELS = {'co', 'or', 'ac', 'go', 'in', 'ne', 'com', 'net', 'org', 'edu', 'gov'}


def access_lifetime():
    return datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME)


def refresh_lifetime():
    return datetime.timedelta(minutes=settings.JWT_REFRESH_TOKEN_LIFETIME)


def jwt_encode(payload, exp_ts):
    """exp_ts: absolute unix timestamp (int) for the exp claim."""
    payload = {
        **payload,
        'iss': 'TempNet',
        'aud': 'TempNet-clients',
        'iat': int(time.time()),
        'exp': int(exp_ts),
    }
    try:
        return jwt.encode(payload, settings.JWT_PRIVATE_KEY, algorithm='RS256')
    except Exception as e:
        print(f"JWT encode error: {str(e)}")
        return None


def create_access_token(user):
    exp_ts = int(time.time() + access_lifetime().total_seconds())
    return jwt_encode({'uid': user.id, 'un': user.username, 'type': 'access'}, exp_ts)


def create_refresh_token(user):
    # one exp value is shared by the JWT, RefreshToken.expires_at and the cookie max_age
    exp_ts = int(time.time() + refresh_lifetime().total_seconds())
    rt = RefreshToken.objects.create(
        user=user,
        expires_at=datetime.datetime.fromtimestamp(exp_ts),  # naive local time (USE_TZ=False)
    )
    return jwt_encode({'uid': user.id, 'jti': str(rt.jti), 'type': 'refresh'}, exp_ts)


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


# ---------------------------------------------------------------------------
# Refresh-token cookie (flags are derived from FRONTEND_URL)
# ---------------------------------------------------------------------------
def _is_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _site_of(host):
    """Approximate registrable domain (no public-suffix list)."""
    if _is_ip(host):
        return host
    labels = host.split('.')
    if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in SECOND_LEVEL_LABELS:
        return '.'.join(labels[-3:])
    return '.'.join(labels[-2:])


def get_cookie_options(request):
    """
    localhost / 127.0.0.1 frontend -> secure=False, SameSite=Lax
    otherwise secure=True; SameSite=Lax when API and frontend share a site, else None
    """
    origin = request.headers.get('Origin')
    if origin not in settings.FRONTEND_ORIGINS:
        origin = settings.FRONTEND_ORIGINS[0]
    frontend_host = urlparse(origin).hostname or ''

    if frontend_host in LOCAL_HOSTS:
        return {'secure': False, 'samesite': 'Lax'}

    api_host, _port = split_domain_port(request.get_host())
    same_site = _site_of(frontend_host) == _site_of(api_host)
    return {'secure': True, 'samesite': 'Lax' if same_site else 'None'}


def set_refresh_cookie(response, request, token):
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        httponly=True,
        max_age=int(refresh_lifetime().total_seconds()),
        **get_cookie_options(request),
    )


def delete_refresh_cookie(response, request):
    response.delete_cookie(REFRESH_COOKIE_NAME, samesite=get_cookie_options(request)['samesite'])
