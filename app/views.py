from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .jwt import *
from .models import *
from .utilities import *
from .serializers import *
from .authentication import JWTAuthentication
import datetime 
# from django.core.mail import EmailMessage
# from app.email_utils import threaded_send_to_email


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


@api_view(['POST'])
def Api_AccessKey(request, cmd):
	username = request.data.get('username')
	password = request.data.get('password')
	saleName = request.data.get('saleName')

	if not username or not password:
		return Response({"error": "Not username or password."}, status=status.HTTP_400_BAD_REQUEST)

	user = authenticate(username=username, password=password)
	if user is None:
		return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)

	if not (user.is_superuser and user.is_staff):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_403_FORBIDDEN)

	if not saleName:
		return Response({"error": "Who is you sale?."}, status=status.HTTP_400_BAD_REQUEST)

	AccessKey.objects.create(sale=saleName)
	return Response({"detail": "created"}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def Api_SignUp(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)
	accessKey = request.data.get('accessKey', None)
	country = request.data.get('country', None)
	mobile = request.data.get('mobile', None)
	# token = request.data.get("captcha_token")
		
	# if not token:
	# 	return Response({"error": "Captcha token not found."}, status=400)

	# is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	# if not is_valid:
	# 	return Response({"error": error}, status=403)

	if not accessKey:
		return Response({"error": "No access."}, status=status.HTTP_400_BAD_REQUEST)
	if not username or not password:
		return Response({"error": "Please send username and password."}, status=status.HTTP_400_BAD_REQUEST)
	if not CheckEmailValidate(username):
		return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)
	if not CheckPasswordValidate(password):
		return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)
	if User.objects.filter(username=username).exists():
		return Response({"error": "Username already exists."}, status=status.HTTP_409_CONFLICT)

	first_name = request.data.get('first_name', '') or ''
	last_name = request.data.get('last_name', '') or ''

	try:
		with transaction.atomic():
			check = AccessKey.objects.select_for_update().filter(key=accessKey).first()
			if check is None:
				return Response({"error": "Not access"}, status=status.HTTP_401_UNAUTHORIZED)
			if check.is_used == True:
				return Response({"error": "Not access"}, status=status.HTTP_401_UNAUTHORIZED)

			user_core = User.objects.create_user(
				username=username,
				password=password,
				first_name=first_name,
				last_name=last_name,
			)
			ProfileUser.objects.create(
				username=user_core,
				first_name=user_core.first_name,
				last_name=user_core.last_name,
				mobile=mobile,
				country=country
			)
			check.user = username
			check.is_used = True
			check.used_at = timezone.now()
			check.save()

	except Exception as e:
		print(f"Error creating user: {str(e)}")
		return Response({"error": "Failed to create user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({"message": "Created success.","username": username,}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def Api_SignIn(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)
	# token = request.data.get("captcha_token")
		
	# if not token:
	# 	return Response({"error": "Captcha token not found."}, status=400)

	# is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	# if not is_valid:
	# 	return Response({"error": error}, status=403)

	if not username or not password:
		return Response({'status': 'Failure', 'message': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

	user = authenticate(username=username, password=password)
	if user is None:
		return Response({'status': 'Failure', 'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)

	profile = ProfileUser.objects.filter(username=user).first()
	if profile is None:
		return Response({'status': 'Failure', 'message': 'User not registered'}, status=status.HTTP_404_NOT_FOUND)

	access_token = create_access_token(user)
	refresh_token = create_refresh_token(user)

	if access_token is None or refresh_token is None:
		return Response({'status': 'Failure', 'message': 'Could not generate token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	response = Response({
		'status': 'Success',
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'access_token': access_token,
	}, status=status.HTTP_200_OK)

	response.set_cookie(
		'refresh_token',
		refresh_token,
		httponly=True,
		secure=True,
		samesite='Lax',
		max_age=7*24*60*60,
	)
	return response


@api_view(['POST'])
def Api_RefreshToken(request, cmd):
	token = request.COOKIES.get('refresh_token')
	if not token:
		return Response({'status': 'Failure', 'message': 'refresh_token required'}, status=status.HTTP_401_UNAUTHORIZED)

	payload = jwt_decode(token)
	if not payload or payload.get('type') != 'refresh':
		return Response({'status': 'Failure', 'message': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

	try:
		rt = RefreshToken.objects.get(jti=payload['jti'], revoked=False)
	except RefreshToken.DoesNotExist:
		return Response({'status': 'Failure', 'message': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

	if rt.expires_at <= timezone.now():
		return Response({'status': 'Failure', 'message': 'Refresh token expired'}, status=status.HTTP_401_UNAUTHORIZED)

	new_access_token = create_access_token(rt.user)
	if new_access_token is None:
		return Response({'status': 'Failure', 'message': 'Could not generate token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({
		'status': 'Success',
		'access_token': new_access_token,
	}, status=status.HTTP_200_OK)


def get_bearer_token(request):
	"""ดึง token จาก header: Authorization: Bearer <token>"""
	auth_header = request.headers.get('Authorization', '')
	if not auth_header.startswith('Bearer '):
		return None
	return auth_header.split(' ', 1)[1].strip()


@api_view(['POST', 'GET'])
def Api_GetFarm(request, cmd):
	access_token = get_bearer_token(request)
	if not access_token:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	payload = jwt_decode(access_token)
	if not payload:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	if payload.get('type') != 'access':
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	uid = payload.get('uid')
	if not uid:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	user = ProfileUser.objects.filter(username__id=uid).first()
	if not user:
		return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

	dt = []
	farmDatas = ProfileFarm.objects.filter(token=user.token)
	for farmData in farmDatas:
		device = ProfileDevice.objects.filter(nameFarm__nameFarm=farmData.nameFarm)
		silonic = ProfileSilonic.objects.filter(nameFarm__nameFarm=farmData.nameFarm)
		egg = ProfileEggAi.objects.filter(nameFarm__nameFarm=farmData.nameFarm)
		userapp = ProfileUserApp.objects.filter(nameFarm__nameFarm=farmData.nameFarm)

		dt.append({
			"farm": ProfileFarmSerializer(farmData).data,
			"device": ProfileDeviceSerializer(device, many=True).data,
			"silonic": ProfileSilonicSerializer(silonic, many=True).data,
			"egg": ProfileEggAiSerializer(egg, many=True).data,
			"userapp": ProfileUserAppSerializer(userapp, many=True).data,
		})

	return Response(dt)


@api_view(['POST','GET'])
def Api_NewFarm(request, cmd):
	access_token = get_bearer_token(request)
	if not access_token:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	payload = jwt_decode(access_token)
	if not payload:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	if payload.get('type') != 'access':
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	uid = payload.get('uid')
	if not uid:
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	user = ProfileUser.objects.filter(username__id=uid).first()
	if not user:
		return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

	if request.method == 'POST':
		if cmd == 'create':
			try:
				with transaction.atomic():
					body = request.data

					farm_data = body.get("farm", {})
					devices = body.get("device", [])
					silonics = body.get("silonic", [])
					eggs = body.get("egg", [])
					users = body.get("userapp", [])

					farm_data = farm_data.copy()
					farm_data.pop("id", None)

					name_farm = farm_data.get("nameFarm")
					if not name_farm:
						return Response(
							{"message": "error", "detail": "กรุณาระบุชื่อฟาร์ม (nameFarm)"},
							status=status.HTTP_400_BAD_REQUEST
						)

					if ProfileFarm.objects.filter(nameFarm=name_farm).exists():
						return Response(
							{"message": "error", "detail": f"ชื่อฟาร์ม '{name_farm}' นี้มีอยู่แล้ว"},
							status=status.HTTP_400_BAD_REQUEST
						)

					farm_data["token"] = str(user.token)

					farm_serializer = ProfileFarmSerializer(data=farm_data)
					farm_serializer.is_valid(raise_exception=True)
					farm_obj = farm_serializer.save()

					devices_update = []
					silonic_update = []
					egg_update = []

					for device in devices:
						new = ProfileDevice(
							nameFarm=farm_obj,
							type=device.get("type"),
							modelTemp=device.get("modelTemp"),
							house=device.get("house", "1"),
							controllerSN=device.get("controllerSN"),
							smartlinkSN=device.get("smartlinkSN"),
						)
						devices_update.append(new)

					for silonic in silonics:
						new = ProfileSilonic(
							nameFarm=farm_obj,
							house=silonic.get("house", "1"),
							serialNumber=silonic.get("serialNumber"),
						)
						silonic_update.append(new)

					for egg in eggs:
						egg = egg.copy()
						egg.pop("id", None)
						egg["nameFarm"] = farm_obj.id
						egg_serializer = ProfileEggAiSerializer(data=egg)
						egg_serializer.is_valid(raise_exception=True)
						egg_serializer.save()

					for u in users:
						u = u.copy()
						u.pop("id", None)
						u["nameFarm"] = farm_obj.id
						user_serializer = ProfileUserAppSerializer(data=u)
						user_serializer.is_valid(raise_exception=True)
						user_serializer.save()

					return Response(
						{"message": "ok", "farm_id": farm_obj.id},
						status=status.HTTP_201_CREATED
					)	

			except serializers.ValidationError as e:
				return Response(
					{"message": "error", "detail": e.detail},
					status=status.HTTP_400_BAD_REQUEST
				)
			except Exception as e:
				return Response(
					{"message": "error", "detail": str(e)},
					status=status.HTTP_400_BAD_REQUEST
				)

		return Response(
			{"message": "error", "detail": f"ไม่รู้จักคำสั่ง cmd='{cmd}'"},
			status=status.HTTP_400_BAD_REQUEST
		)

	return Response(
		{"message": "error", "detail": "Method not allowed for this cmd"},
		status=status.HTTP_405_METHOD_NOT_ALLOWED
	)