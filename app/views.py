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
import logging

# from django.core.mail import EmailMessage
# from app.email_utils import threaded_send_to_email
logger = logging.getLogger(__name__)

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

	ass = AccessKey.objects.create(sale=saleName)
	return Response({"detail": "created", "key":ass.key}, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def CheckKey(request, cmd):
	accessKey = request.data.get('accessKey', None)

	with transaction.atomic():
		if not accessKey:
			return Response({"error": "No access."}, status=status.HTTP_400_BAD_REQUEST)

		check = AccessKey.objects.select_for_update().filter(key=accessKey).first()

		if check is None:
			return Response({"error": "Not access"}, status=status.HTTP_401_UNAUTHORIZED)
		if check.is_used == True:
			return Response({"error": "Not access"}, status=status.HTTP_401_UNAUTHORIZED)

	return Response({"message": "Access key is True."})

	

@api_view(['POST'])
@permission_classes([AllowAny])
def Api_SignUp(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)
	accessKey = request.data.get('accessKey', None)
	country = request.data.get('country', None)
	mobile = request.data.get('mobile', None)
	token = request.data.get("captcha_token")
		
	# if not token:
	# 	return Response({"error": "Captcha token not found."}, status=400)

	# is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	# if not is_valid:
	# 	return Response({"error": error}, status=403)

	if not accessKey:
		return Response({"error": "No access."}, status=status.HTTP_400_BAD_REQUEST)
	if not username or not password:
		return Response({"error": "Please send username and password."}, status=status.HTTP_400_BAD_REQUEST)
	# if not CheckEmailValidate(username):
	# 	return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)
	# if not CheckPasswordValidate(password):
	# 	return Response({"error": "Username or Password must be a valid."}, status=status.HTTP_401_UNAUTHORIZED)
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

	# models_qs = ModelController.objects.values('model')
	# ip_qs = ModelIpAddress.objects.select_related('model').values('model__model', 'ipAddress')

	response = Response({
		'status': 'Success',
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,		
		'access_token': access_token,
		# 'models': list(models_qs),
		# 'ip_addresses': list(ip_qs),
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

	if cmd == "user":
		farm_queryset = (
			ProfileFarm.objects.filter(user=user).prefetch_related(
				"devices",
				"alarms",
				"silonics",
				"eggs",
				"userapps",
			))

	elif cmd == "admin":

		if not (user.username.is_superuser and user.username.is_staff):
			return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_403_FORBIDDEN,)

		farm_queryset = (ProfileFarm.objects.select_related("user").prefetch_related(
				"devices",
				"alarms",
				"silonics",
				"eggs",
				"userapps",
			))

	data = []
	if farm_queryset:
		for farm in farm_queryset:
			data.append({
				"farm": ProfileFarmSerializer(farm).data,
				"device": ProfileDeviceSerializer(farm.devices.all(), many=True).data,
				"alarm": ProfileAlarmSerializer(farm.alarms.all(), many=True).data,
				"silonic": ProfileSilonicSerializer(farm.silonics.all(), many=True).data,
				"egg": ProfileEggSerializer(farm.eggs.all(),many=True,).data,
				"userapp": ProfileUserAppSerializer(farm.userapps.all(), many=True).data,
			})
		return Response(data, status=status.HTTP_200_OK)

	return Response({"message": "error", "detail": "Unknown cmd."}, status=status.HTTP_400_BAD_REQUEST)

class RequestFarmFail(Exception):
	def __init__(self, detail, status=status.HTTP_400_BAD_REQUEST):
		self.detail = detail
		self.status = status
		super().__init__(str(detail))

@api_view(['POST','GET'])
def Api_RequestFarm(request, cmd):
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

					if not isinstance(body, dict):
						raise RequestFarmFail({"message": "error", "detail": "Data not object."}, status=status.HTTP_400_BAD_REQUEST)

					farm_data = body.get("farm", {})
					devices = body.get("device", [])
					silonics = body.get("silonic", [])
					eggs = body.get("egg", [])
					alarms = body.get("alarm", [])
					users = body.get("userapp", [])

					name_farm = farm_data.get("nameFarm")
					if not name_farm:
						raise RequestFarmFail({"message": "error", "detail": "No farm name."}, status=status.HTTP_400_BAD_REQUEST)

					if ProfileFarm.objects.filter(nameFarm=name_farm).exists():
						raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system1."}, status=status.HTTP_400_BAD_REQUEST)

					farm_serializer = ProfileFarmSerializer(data=farm_data)
					farm_serializer.is_valid(raise_exception=True)
					farm_obj = farm_serializer.save(user=user, status=StatusChoices.PENDING)

					devices_create = []
					silonics_create = []
					eggs_create = []
					alarms_create = []
					users_create = []

					seen_controller_sn = set()
					seen_smartlink_sn = set()
					seen_silonic_sn = set()
					seen_egg_sn = set()
					seen_alarm_sn = set()
					seen_usernames = set()

					# ---- Device ----
					for device in devices:
						controller_sn = device.get("controllerSN")
						smartlink_sn = device.get("smartlinkSN")

						if controller_sn:
							if controller_sn in seen_controller_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_controller_sn.add(controller_sn)

							if ProfileDevice.objects.filter(controllerSN=controller_sn).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system2."}, status=status.HTTP_400_BAD_REQUEST)

						if smartlink_sn:
							if smartlink_sn in seen_smartlink_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)

							seen_smartlink_sn.add(smartlink_sn)

							if ProfileDevice.objects.filter(smartlinkSN=smartlink_sn).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system3."}, status=status.HTTP_400_BAD_REQUEST)

						new = ProfileDevice(
							nameFarm=farm_obj,
							type=device.get("type"),
							modelTemp=device.get("modelTemp"),
							house=device.get("house", "1"),
							controllerSN=device.get("controllerSN"),
							smartlinkSN=device.get("smartlinkSN"),
						)
						devices_create.append(new)

					# ---- Silonic ----
					for silonic in silonics:
						serial_number = silonic.get("serialNumber")

						if serial_number:
							if serial_number in seen_silonic_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_silonic_sn.add(serial_number)

							if ProfileSilonic.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system4."}, status=status.HTTP_400_BAD_REQUEST)

						new = ProfileSilonic(
							nameFarm=farm_obj,
							type=silonic.get("type"),
							house=silonic.get("house", "1"),
							serialNumber=silonic.get("serialNumber"),
						)
						silonics_create.append(new)

					# ---- Egg (ProfileEgg) ----
					for egg in eggs:
						serial_number = egg.get("serialNumber")

						if serial_number:
							if serial_number in seen_egg_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_egg_sn.add(serial_number)

							if ProfileEgg.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system5."}, status=status.HTTP_400_BAD_REQUEST)

						new = ProfileEgg(
							nameFarm=farm_obj,
							type=egg.get("type"),
							modelEgg=egg.get("modelEgg"),
							house=egg.get("house", "1"),
							serialNumber=egg.get("serialNumber"),
						)
						eggs_create.append(new)

					# ---- Alarm ----
					for alarm in alarms:
						serial_number = alarm.get("serialNumber")

						if serial_number:
							if serial_number in seen_alarm_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_alarm_sn.add(serial_number)

							if ProfileAlarm.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system6."}, status=status.HTTP_400_BAD_REQUEST)

						new = ProfileAlarm(
							nameFarm=farm_obj,
							type=alarm.get("type"),
							modelAlarm=alarm.get("modelAlarm"),
							house=alarm.get("house", "1"),
							serialNumber=alarm.get("serialNumber"),
						)
						alarms_create.append(new)

					# ---- UserApp ----
					for u in users:
						username = u.get("username")

						if username:
							if username in seen_usernames:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_usernames.add(username)

							if ProfileUserApp.objects.filter(username=username).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system7."}, status=status.HTTP_400_BAD_REQUEST)

						new = ProfileUserApp(
							nameFarm=farm_obj,
							username=u.get("username"),
							userType=u.get("userType"),
							userEmail=u.get("userEmail"),
						)
						users_create.append(new)

					if devices_create:
						ProfileDevice.objects.bulk_create(devices_create)

					if silonics_create:
						ProfileSilonic.objects.bulk_create(silonics_create)

					if eggs_create:
						ProfileEgg.objects.bulk_create(eggs_create)

					if alarms_create:
						ProfileAlarm.objects.bulk_create(alarms_create)

					if users_create:
						ProfileUserApp.objects.bulk_create(users_create)

				return Response({"message": "ok", "farm_id": farm_obj.id}, status=status.HTTP_201_CREATED)

			except RequestFarmFail as e:
				return Response(e.detail, status=e.status)

			except serializers.ValidationError as e:
				return Response({"message": "error", "detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				logger.exception("Api_RequestFarm unexpected error")
				return Response({"message": "error","detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		# ================= UPDATE =================
		elif cmd == 'update':
			try:
				with transaction.atomic():
					body = request.data

					if not isinstance(body, dict):
						raise RequestFarmFail({"message": "error", "detail": "Data not object."}, status=status.HTTP_400_BAD_REQUEST)

					farm_data = body.get("farm", {})
					devices = body.get("device", [])
					silonics = body.get("silonic", [])
					eggs = body.get("egg", [])
					alarms = body.get("alarm", [])
					users = body.get("userapp", [])

					name_farm = farm_data.get("nameFarm")
					if not name_farm:
						raise RequestFarmFail({"message": "error", "detail": "No farm name."}, status=status.HTTP_400_BAD_REQUEST)

					farm_obj = ProfileFarm.objects.filter(nameFarm=name_farm, user=user).first()
					if not farm_obj:
						raise RequestFarmFail({"message": "error", "detail": "This data does not exist in the system."}, status=status.HTTP_404_NOT_FOUND)

					farm_data = farm_data.copy()
					farm_data.pop("id", None)
					farm_data.pop("nameFarm", None)

					farm_serializer = ProfileFarmSerializer(farm_obj, data=farm_data, partial=True)
					farm_serializer.is_valid(raise_exception=True)
					farm_obj = farm_serializer.save(status=StatusChoices.EDIT, date_edit=timezone.now())

					seen_controller_sn = set()
					seen_smartlink_sn = set()
					seen_silonic_sn = set()
					seen_egg_sn = set()
					seen_alarm_sn = set()
					seen_usernames = set()

					kept_device_ids = []
					kept_silonic_ids = []
					kept_egg_ids = []
					kept_alarm_ids = []
					kept_user_ids = []

					# ---- Device ----
					for device in devices:
						controller_sn = device.get("controllerSN")
						smartlink_sn = device.get("smartlinkSN")

						if controller_sn:
							if controller_sn in seen_controller_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_controller_sn.add(controller_sn)

						if smartlink_sn:
							if smartlink_sn in seen_smartlink_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_smartlink_sn.add(smartlink_sn)

						existing = None
						if controller_sn:
							existing = ProfileDevice.objects.filter(controllerSN=controller_sn, nameFarm=farm_obj).first()
						if not existing and smartlink_sn:
							existing = ProfileDevice.objects.filter(smartlinkSN=smartlink_sn, nameFarm=farm_obj).first()

						if existing:
							if controller_sn and ProfileDevice.objects.filter(controllerSN=controller_sn).exclude(id=existing.id).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)
							if smartlink_sn and ProfileDevice.objects.filter(smartlinkSN=smartlink_sn).exclude(id=existing.id).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							existing.type = device.get("type", existing.type)
							existing.modelTemp = device.get("modelTemp", existing.modelTemp)
							existing.house = device.get("house", existing.house)
							existing.controllerSN = controller_sn if controller_sn is not None else existing.controllerSN
							existing.smartlinkSN = smartlink_sn if smartlink_sn is not None else existing.smartlinkSN
							existing.save()
							kept_device_ids.append(existing.id)
						else:
							if controller_sn and ProfileDevice.objects.filter(controllerSN=controller_sn).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)
							if smartlink_sn and ProfileDevice.objects.filter(smartlinkSN=smartlink_sn).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							new_device = ProfileDevice.objects.create(
								nameFarm=farm_obj,
								type=device.get("type"),
								modelTemp=device.get("modelTemp"),
								house=device.get("house", "1"),
								controllerSN=controller_sn,
								smartlinkSN=smartlink_sn,
							)
							kept_device_ids.append(new_device.id)

					ProfileDevice.objects.filter(nameFarm=farm_obj).exclude(id__in=kept_device_ids).delete()

					# ---- Silonic ----
					for silonic in silonics:
						serial_number = silonic.get("serialNumber")

						if serial_number:
							if serial_number in seen_silonic_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_silonic_sn.add(serial_number)

						existing = ProfileSilonic.objects.filter(serialNumber=serial_number, nameFarm=farm_obj).first() if serial_number else None

						if existing:
							existing.type = silonic.get("type", existing.type)
							existing.house = silonic.get("house", existing.house)
							existing.save()
							kept_silonic_ids.append(existing.id)
						else:
							if serial_number and ProfileSilonic.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							new_silonic = ProfileSilonic.objects.create(
								nameFarm=farm_obj,
								type=silonic.get("type"),
								house=silonic.get("house", "1"),
								serialNumber=serial_number,
							)
							kept_silonic_ids.append(new_silonic.id)

					ProfileSilonic.objects.filter(nameFarm=farm_obj).exclude(id__in=kept_silonic_ids).delete()

					# ---- Egg (ProfileEgg) ----
					for egg in eggs:
						serial_number = egg.get("serialNumber")

						if serial_number:
							if serial_number in seen_egg_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_egg_sn.add(serial_number)

						existing = ProfileEgg.objects.filter(serialNumber=serial_number, nameFarm=farm_obj).first() if serial_number else None

						if existing:
							existing.type = egg.get("type", existing.type)
							existing.modelEgg = egg.get("modelEgg", existing.modelEgg)
							existing.house = egg.get("house", existing.house)
							existing.save()
							kept_egg_ids.append(existing.id)
						else:
							if serial_number and ProfileEgg.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							new_egg = ProfileEgg.objects.create(
								nameFarm=farm_obj,
								type=egg.get("type"),
								modelEgg=egg.get("modelEgg"),
								house=egg.get("house", "1"),
								serialNumber=serial_number,
							)
							kept_egg_ids.append(new_egg.id)

					ProfileEgg.objects.filter(nameFarm=farm_obj).exclude(id__in=kept_egg_ids).delete()

					# ---- Alarm ----
					for alarm in alarms:
						serial_number = alarm.get("serialNumber")

						if serial_number:
							if serial_number in seen_alarm_sn:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_alarm_sn.add(serial_number)

						existing = ProfileAlarm.objects.filter(serialNumber=serial_number, nameFarm=farm_obj).first() if serial_number else None

						if existing:
							existing.type = alarm.get("type", existing.type)
							existing.modelAlarm = alarm.get("modelAlarm", existing.modelAlarm)
							existing.house = alarm.get("house", existing.house)
							existing.save()
							kept_alarm_ids.append(existing.id)
						else:
							if serial_number and ProfileAlarm.objects.filter(serialNumber=serial_number).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							new_alarm = ProfileAlarm.objects.create(
								nameFarm=farm_obj,
								type=alarm.get("type"),
								modelAlarm=alarm.get("modelAlarm"),
								house=alarm.get("house", "1"),
								serialNumber=serial_number,
							)
							kept_alarm_ids.append(new_alarm.id)

					ProfileAlarm.objects.filter(nameFarm=farm_obj).exclude(id__in=kept_alarm_ids).delete()

					# ---- UserApp ----
					for u in users:
						username = u.get("username")

						if username:
							if username in seen_usernames:
								raise RequestFarmFail({"message": "error", "detail": "The submitted data is duplicated."}, status=status.HTTP_400_BAD_REQUEST)
							seen_usernames.add(username)

						existing = ProfileUserApp.objects.filter(username=username, nameFarm=farm_obj).first() if username else None

						if existing:
							existing.userType = u.get("userType", existing.userType)
							existing.userEmail = u.get("userEmail", existing.userEmail)
							existing.save()
							kept_user_ids.append(existing.id)
						else:
							if username and ProfileUserApp.objects.filter(username=username).exists():
								raise RequestFarmFail({"message": "error", "detail": "This data already exists in the system."}, status=status.HTTP_400_BAD_REQUEST)

							new_user = ProfileUserApp.objects.create(
								nameFarm=farm_obj,
								username=username,
								userType=u.get("userType"),
								userEmail=u.get("userEmail"),
							)
							kept_user_ids.append(new_user.id)

					ProfileUserApp.objects.filter(nameFarm=farm_obj).exclude(id__in=kept_user_ids).delete()

				return Response({"message": "ok", "farm_id": farm_obj.id}, status=status.HTTP_200_OK)

			except RequestFarmFail as e:
				return Response(e.detail, status=e.status)

			except serializers.ValidationError as e:
				return Response({"message": "error", "detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

			except Exception as e:
				logger.exception("Api_RequestFarm unexpected error")
				return Response({"message": "error","detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response({"message": "error", "detail": "Unknow cmd"}, status=status.HTTP_400_BAD_REQUEST)

	return Response({"message": "error", "detail": "Method not allowed for this cmd"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)