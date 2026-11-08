import datetime
import logging
import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .farm_function import *
from .jwt import (
	REFRESH_COOKIE_NAME,
	create_access_token,
	create_refresh_token,
	delete_refresh_cookie,
	jwt_decode,
	set_refresh_cookie,
)
from .models import *
from .serializers import *
from .utilities import CheckEmailValidate, CheckPasswordValidate, verify_captcha

# from django.core.mail import EmailMessage
# from app.email_utils import threaded_send_to_email
logger = logging.getLogger(__name__)
LOGIN_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9]+")

class SignInRateThrottle(ScopedRateThrottle):
	scope = 'signin'

class TempNetResponseMsg:
	NO_TOKEN		 	 = {'status': 'Not Found', 'message': 'No Token'}
	NO_HOUSE		 	 = {'status': 'Not Found', 'message': 'No house number'}
	NO_LOT			 	 = {'status': 'Not Found', 'message': 'No Lot. data'}
	NO_PERM			 	 = {'status': 'Failure', 'message': 'The token contains no permissions'}
	INVALID_TYPE	 	 = {'status': 'Failure', 'message': 'Invalid value type'}
	EXPIRED			 	 = {'status': 'Failure', 'message': 'This house is expired'}
	NO_DATA			 	 = {'status': 'Not Found', 'message': 'No data'}
	STOPPED			 	 = {'status': 'Failure', 'message': 'This house is stopped'}
	NO_MORE_1DAY		 = {'status': 'Failure', 'message': 'The date must be within 1 day'}
	NO_EMAIL			 = {'status': 'Failure', 'message': 'No Email or invalid email'}
	NO_USER		 		 = {'status': 'Not Found', 'message': 'No user'}
	NO_STARTDATE 		 = {'status': 'Failure', 'message': 'No startDate'}
	INVALID_ADDR 		 = {'status': 'Failure', 'message': 'Invalid Address'}
	NO_FAN		 		 = {'status': 'Not Found', 'message': 'No Fan'}
	NO_SPF		 		 = {'status': 'Not Found', 'message': 'No SpeedFan'}
	FILE_ERR	 		 = {'status': 'Failure', 'message': 'File input error'}
	CSV_ONLY	 		 = {'status': 'Failure', 'message': 'Supported CSV only'}
	FIELD_ERR	 		 = {'status': 'Failure', 'message': 'Field name error'}
	NO_DATETIME 		 = {'status': 'Failure', 'message': 'No date_time or invalid date_time'}



def is_admin_user(user):
	return bool(user and user.is_superuser and user.is_staff)


def get_profile(request):
	return ProfileUser.objects.filter(username=request.user).first()


def get_admin_only_response(request):
	"""None when the caller is an admin, otherwise a 403 Response."""
	if not is_admin_user(request.user):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_403_FORBIDDEN)
	return None


def access_key_problem(access_key_obj):
	"""Return an error Response for a missing/used/expired key, else None."""
	if access_key_obj is None or access_key_obj.is_used:
		return Response({"error": "Not access"}, status=status.HTTP_401_UNAUTHORIZED)
	if access_key_obj.expired_at <= timezone.now():
		return Response({"error": "Access key expired."}, status=status.HTTP_401_UNAUTHORIZED)
	return None


def signup_conflict(login_username, email):
	if (
		ProfileUser.objects.filter(login_username=login_username).exists()
		or User.objects.filter(username__iexact=login_username).exists()
	):
		return "username_taken", "Username already exists."
	if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
		return "email_taken", "Email already exists."
	return None


def signup_conflict_response(conflict):
	code, message = conflict
	return Response({"code": code, "error": message}, status=status.HTTP_409_CONFLICT)


def resolve_login_username(identifier, admin_login):
	if "@" in identifier:
		# Existing customer accounts use their email as the Django username.
		users = User.objects.filter(username__iexact=identifier)
		if not users.exists():
			users = User.objects.filter(email__iexact=identifier)
		matches = list(users.values_list("username", flat=True)[:2])
		return matches[0] if len(matches) == 1 else identifier

	# Native Django admin accounts retain priority on the admin entry point.
	if admin_login and User.objects.filter(username=identifier).exists():
		return identifier
	if not LOGIN_USERNAME_PATTERN.fullmatch(identifier):
		return identifier
	profile = ProfileUser.objects.select_related("username").filter(login_username=identifier.lower()).first()
	return profile.username.username if profile else identifier


# ==== AUTH ====================================================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def Api_AccessKey(request, cmd):
	username = request.data.get('username')
	password = request.data.get('password')
	saleName = request.data.get('saleName')

	if not username or not password:
		return Response({"error": "Not username or password."}, status=status.HTTP_400_BAD_REQUEST)

	user = authenticate(username=username, password=password)
	if user is None:
		return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)

	if not is_admin_user(user):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_403_FORBIDDEN)

	if not saleName:
		return Response({"error": "Who is you sale?."}, status=status.HTTP_400_BAD_REQUEST)

	ass = AccessKey.objects.create(sale=saleName)
	return Response({"detail": "created", "key": ass.key}, status=201)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def CheckKey(request, cmd):
	accessKey = request.data.get('accessKey', None)
	if not accessKey:
		return Response({"error": "No access."}, status=status.HTTP_400_BAD_REQUEST)

	check = AccessKey.objects.filter(key=accessKey).first()
	problem = access_key_problem(check)
	if problem:
		return problem

	return Response({"message": "Access key is True."})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def Api_SignUp(request, cmd):
	username = request.data.get('username', None)
	email = request.data.get('email', None)
	password = request.data.get('password', None)
	accessKey = request.data.get('accessKey', None)
	country = request.data.get('country', None)
	mobile = request.data.get('mobile', None)
	token = request.data.get("captcha_token")

	if not token:
		return Response({"error": "Captcha token not found."}, status=400)

	is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	if not is_valid:
		return Response({"error": error}, status=403)

	if not accessKey:
		return Response({"error": "No access."}, status=status.HTTP_400_BAD_REQUEST)
	if (
		not isinstance(username, str)
		or len(username) > ProfileUser.LOGIN_USERNAME_MAX_LENGTH
		or not LOGIN_USERNAME_PATTERN.fullmatch(username)
	):
		return Response({"code": "invalid_username", "error": "Use 1–50 English letters or digits for the username."}, status=status.HTTP_400_BAD_REQUEST)
	username = username.lower()
	if not isinstance(email, str) or len(email.strip()) > 150 or not CheckEmailValidate(email.strip()):
		return Response({"code": "invalid_email", "error": "Enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)
	email = email.strip().lower()
	if not isinstance(password, str) or not CheckPasswordValidate(password):
		return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)
	if not country or country not in ModelCountryChoices.values:
		return Response({"error": "Invalid country."}, status=status.HTTP_400_BAD_REQUEST)
	conflict = signup_conflict(username, email)
	if conflict:
		return signup_conflict_response(conflict)

	first_name = request.data.get('first_name', '') or ''
	last_name = request.data.get('last_name', '') or ''

	try:
		with transaction.atomic():
			check = AccessKey.objects.select_for_update().filter(key=accessKey).first()
			problem = access_key_problem(check)
			if problem:
				return problem

			user_core = User.objects.create_user(
				username=email,
				email=email,
				password=password,
				first_name=first_name,
				last_name=last_name,
			)
			ProfileUser.objects.create(
				username=user_core,
				login_username=username,
				first_name=user_core.first_name,
				last_name=user_core.last_name,
				mobile=mobile,
				country=country
			)
			check.user = username
			check.is_used = True
			check.used_at = timezone.now()
			check.save()

	except IntegrityError:
		# Another signup may have claimed the username or email after the initial check.
		conflict = signup_conflict(username, email)
		if conflict:
			return signup_conflict_response(conflict)
		logger.exception("Integrity error during signup")
		return Response({"error": "Failed to create user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	except Exception:
		logger.exception("Error creating user during signup")
		return Response({"error": "Failed to create user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({"message": "Created success.", "username": username, }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([SignInRateThrottle])
def Api_SignIn(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)
	token = request.data.get("captcha_token")

	if not token:
		return Response({"error": "Captcha token not found."}, status=400)

	is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	if not is_valid:
		return Response({"error": error}, status=403)

	if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or not password:
		return Response({'status': 'Failure', 'message': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

	login_username = resolve_login_username(username.strip(), admin_login=(cmd == "admin"))
	user = authenticate(request, username=login_username, password=password)
	if user is None:
		return Response({'status': 'Failure', 'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)

	admin = is_admin_user(user)
	if cmd == "admin" and not admin:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_403_FORBIDDEN)

	# admins (createsuperuser) do not need a ProfileUser to sign in
	profile = getattr(user, "profileuser", None)
	if not admin and profile is None:
		return Response({'status': 'Failure', 'message': 'User not registered'}, status=status.HTTP_404_NOT_FOUND)

	access_token = create_access_token(user)
	refresh_token = create_refresh_token(user)

	if access_token is None or refresh_token is None:
		return Response({'status': 'Failure', 'message': 'Could not generate token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	response = Response({
		'status': 'Success',
		**ProfileUser.account_identity(user, profile),
		'first_name': user.first_name,
		'last_name': user.last_name,
		'is_admin': admin,
		'access_token': access_token,
	}, status=status.HTTP_200_OK)

	set_refresh_cookie(response, request, refresh_token)
	return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def Api_RefreshToken(request, cmd):
	token = request.COOKIES.get(REFRESH_COOKIE_NAME)
	if not token:
		return Response({'status': 'Failure', 'message': 'refresh_token required'}, status=status.HTTP_401_UNAUTHORIZED)

	payload = jwt_decode(token)
	if not payload or payload.get('type') != 'refresh':
		return Response({'status': 'Failure', 'message': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

	rt = RefreshToken.objects.select_related('user').filter(jti=payload.get('jti'), revoked=False).first()
	if rt is None or rt.user_id != payload.get('uid') or not rt.user.is_active:
		return Response({'status': 'Failure', 'message': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

	if rt.expires_at <= timezone.now():
		return Response({'status': 'Failure', 'message': 'Refresh token expired'}, status=status.HTTP_401_UNAUTHORIZED)

	new_access_token = create_access_token(rt.user)
	if new_access_token is None:
		return Response({'status': 'Failure', 'message': 'Could not generate token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({
		'status': 'Success',
		**ProfileUser.account_identity(rt.user, getattr(rt.user, "profileuser", None)),
		'is_admin': is_admin_user(rt.user),
		'access_token': new_access_token,
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def Api_Logout(request, cmd):
	"""Revoke the refresh token (if any) and clear the cookie. Always 200 so sign-out never gets stuck."""
	token = request.COOKIES.get(REFRESH_COOKIE_NAME)
	payload = jwt_decode(token) if token else None
	if payload and payload.get('type') == 'refresh' and payload.get('jti'):
		RefreshToken.objects.filter(jti=payload['jti']).update(revoked=True)

	response = Response({'status': 'Success'}, status=status.HTTP_200_OK)
	delete_refresh_cookie(response, request)
	return response

# ==== FARM ====================================================================
def farm_error_response(exc):
    """Convert exceptions raised while handling a farm request into the standard error Response."""
    if isinstance(exc, RequestFarmFail):
        return Response(exc.detail, status=exc.http_status)
    if isinstance(exc, serializers.ValidationError):
        return Response({"message": "error", "detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, IntegrityError):
        logger.exception("Farm request integrity error")
        return Response(
            {"message": "error", "detail": "Duplicate data (farm name, serial number or username is already in use)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    logger.exception("Farm request unexpected error")
    return Response({"message": "error", "detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def serialize_farm(farm):
    """One farm + child rows (uses prefetched relations, ids included)."""
    return {
        "farm": ProfileFarmSerializer(farm).data,
        "device": ProfileDeviceSerializer(farm.devices.all(), many=True).data,
        "alarm": ProfileAlarmSerializer(farm.alarms.all(), many=True).data,
        "silonic": ProfileSilonicSerializer(farm.silonics.all(), many=True).data,
        "egg": ProfileEggSerializer(farm.eggs.all(), many=True).data,
        "userapp": ProfileUserAppSerializer(farm.userapps.all(), many=True).data,
    }


def farm_queryset_with_children():
    return (
        ProfileFarm.objects.select_related("user__username")
        .prefetch_related("devices", "alarms", "silonics", "eggs", "userapps")
        .order_by("-date_created")
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Api_EquipmentModels(request):
    queryset = EquipmentModel.objects.all()
    category = normalize_blank(request.query_params.get("category"))
    if category:
        category = category.upper()
        if category not in EquipmentCategory.values:
            request_fail_response = {"message": "error", "detail": "Invalid category. Must be one of: " + ", ".join(EquipmentCategory.values)}
            return Response(request_fail_response, status=status.HTTP_400_BAD_REQUEST)
        queryset = queryset.filter(category=category)
    return Response(EquipmentModelSerializer(queryset, many=True).data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def Api_GetFarm(request, cmd):
    if cmd == "user":
        profile = get_profile(request)
        if profile is None:
            # admin accounts created by createsuperuser have no ProfileUser and no farms
            if is_admin_user(request.user):
                return Response([], status=status.HTTP_200_OK)
            return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)
        farm_queryset = farm_queryset_with_children().filter(user=profile)

    elif cmd == "admin":
        denied = get_admin_only_response(request)
        if denied:
            return denied
        farm_queryset = farm_queryset_with_children()

    else:
        return Response({"message": "error", "detail": "Unknown cmd."}, status=status.HTTP_400_BAD_REQUEST)

    return Response([serialize_farm(farm) for farm in farm_queryset], status=status.HTTP_200_OK)


EDITABLE_BY_CUSTOMER = (StatusChoices.PENDING, StatusChoices.EDIT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Api_RequestFarm(request, cmd):
    profile = get_profile(request)
    if profile is None:
        return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

    try:
        with transaction.atomic():
            body = request.data
            if not isinstance(body, dict):
                request_fail("Data not object.")

            farm_data = body.get("farm", {})
            if not isinstance(farm_data, dict):
                request_fail("'farm' must be an object.")

            if cmd == "create":
                farm_obj = create_farm(farm_data, profile, ProfileFarmSerializer)
                sync_farm_children(farm_obj, body)
                return Response({"message": "ok", "farm_id": farm_obj.id}, status=status.HTTP_201_CREATED)

            if cmd == "update":
                farm_id = to_int(farm_data.get("id"), "farm id")
                if not farm_id:
                    request_fail("No farm id.")

                farm_obj = ProfileFarm.objects.select_for_update().filter(id=farm_id, user=profile).first()
                if not farm_obj:
                    request_fail("Farm not found.", http_status=status.HTTP_404_NOT_FOUND)
                if farm_obj.status not in EDITABLE_BY_CUSTOMER:
                    request_fail(
                        f"This farm can no longer be edited (status: {farm_obj.status}).",
                        http_status=status.HTTP_403_FORBIDDEN,
                    )

                farm_obj = update_farm(farm_obj, farm_data, ProfileFarmSerializer, new_status=StatusChoices.EDIT)
                sync_farm_children(farm_obj, body)
                return Response({"message": "ok", "farm_id": farm_obj.id}, status=status.HTTP_200_OK)

            request_fail("Unknown cmd.")
    except Exception as e:
        return farm_error_response(e)


# ==== ADMIN FARM ==============================================================
def get_farm_for_admin(farm_id):
    """Lock and return the farm (any owner), or raise a 404 RequestFarmFail."""
    farm_obj = ProfileFarm.objects.select_for_update().filter(id=farm_id).first()
    if not farm_obj:
        request_fail("Farm not found.", http_status=status.HTTP_404_NOT_FOUND)
    return farm_obj


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Api_AdminFarmStatus(request, farm_id, cmd):
    """Approve / reject a farm. Allowed from any status so an admin can change a decision."""
    denied = get_admin_only_response(request)
    if denied:
        return denied

    try:
        with transaction.atomic():
            farm_obj = get_farm_for_admin(farm_id)
            if cmd == "approve":
                farm_obj.status = StatusChoices.APPROVE
            elif cmd == "reject":
                farm_obj.status = StatusChoices.REJECT
            else:
                request_fail("Unknown cmd.")
            farm_obj.save(update_fields=["status"])

            if cmd == "approve":
                on_farm_approved(farm_obj)

            return Response({"message": "ok", "farm_id": farm_obj.id, "status": farm_obj.status}, status=status.HTTP_200_OK)
    except Exception as e:
        return farm_error_response(e)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def Api_AdminFarmDelete(request, farm_id):
    """Delete a farm; devices/alarms/eggs/silonics/app users are removed by cascade."""
    denied = get_admin_only_response(request)
    if denied:
        return denied

    try:
        with transaction.atomic():
            farm_obj = get_farm_for_admin(farm_id)
            farm_obj.delete()
            return Response({"message": "ok", "farm_id": int(farm_id)}, status=status.HTTP_200_OK)
    except Exception as e:
        return farm_error_response(e)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Api_AdminRequestUpdate(request):
    """Admin edit of any farm (any status, any owner). Same payload as /api/request/update; status is kept."""
    denied = get_admin_only_response(request)
    if denied:
        return denied

    try:
        with transaction.atomic():
            body = request.data
            if not isinstance(body, dict):
                request_fail("Data not object.")

            farm_data = body.get("farm", {})
            if not isinstance(farm_data, dict):
                request_fail("'farm' must be an object.")

            farm_id = to_int(farm_data.get("id"), "farm id")
            if not farm_id:
                request_fail("No farm id.")

            farm_obj = get_farm_for_admin(farm_id)
            farm_obj = update_farm(farm_obj, farm_data, ProfileFarmSerializer, new_status=None)
            sync_farm_children(farm_obj, body)
            return Response({"message": "ok", "farm_id": farm_obj.id}, status=status.HTTP_200_OK)
    except Exception as e:
        return farm_error_response(e)
