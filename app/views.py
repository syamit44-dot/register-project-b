from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
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
def Api_SignUp(request, cmd):
	token = request.data.get("captcha_token")
	print (token)	
		
	if not token:
		return Response({"error": "Captcha token not found."}, status=400)

	is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	if not is_valid:
		return Response({"error": error}, status=403)

	username = request.data.get('username', None)
	password = request.data.get('password', None)

	if not username or not password:
		return Response({"error": "Please send username and password."}, status=status.HTTP_400_BAD_REQUEST)
	if not CheckEmailValidate(username):
		return Response({"error": "Username must be a valid email."}, status=status.HTTP_400_BAD_REQUEST)
	if not CheckPasswordValidate(password):
		return Response({"error": "Password must contain only English letters, numbers, and the allowed special characters (! @ # $ % ^ & * ( ) - _ + = ? . ,)."}, status=status.HTTP_400_BAD_REQUEST)
	if User.objects.filter(username=username).exists():
		return Response({"error": "Username already exists."}, status=status.HTTP_409_CONFLICT)

	first_name = request.data.get('first_name', '') or ''
	last_name = request.data.get('last_name', '') or ''

	try:
		with transaction.atomic():
			user_core = User.objects.create_user(
				username=username,
				password=password,
				first_name=first_name,
				last_name=last_name,
			)
			# profile = ProfileUser.objects.create( #สำหรับ signUp + signIn
			ProfileUser.objects.create(
				username=user_core,
				first_name=user_core.first_name,
				last_name=user_core.last_name,
			)
	except Exception as e:
		print(f"Error creating user: {str(e)}")
		return Response({"error": "Failed to create user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#----------สำหรับ signUp + signIn-----------------------------------------------------------------------------------------------|
	# now = timezone.now()
	# payload = {
	# 	'uid': user_core.id,
	# 	'un': user_core.username,
	# 	'exp': int((now + datetime.timedelta(hours=1)).timestamp()),
	# 	'iat': int(now.timestamp()),
	# }
	# access_token = jwt_encode(payload)
	# if access_token is None:
	# 	return Response({"error": "User created but failed to generate token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	# return Response({
	# 	"message": "Created success.",
	# 	"username": username,
	# 	"token": access_token,
	# 	"farm_token": str(profile.token),
	# }, status=status.HTTP_201_CREATED)
#------------------------------------------------------------------------------------------------------------------------------|
	return Response({"message": "Created success.","username": username,}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def Api_SignIn(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)

	if not username or not password:
		return Response({'status': 'Failure', 'message': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

	user = authenticate(username=username, password=password)
	if user is None:
		return Response({'status': 'Failure', 'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)

	profile = ProfileUser.objects.filter(username=user).first()
	if profile is None:
		return Response({'status': 'Failure', 'message': 'User not registered'}, status=status.HTTP_404_NOT_FOUND)

	now = timezone.now()
	payload = {
		'uid': user.id,
		'un': user.username,
		'exp': int((now + datetime.timedelta(hours=1)).timestamp()),
		'iat': int(now.timestamp()),
	}
	access_token = jwt_encode(payload)
	if access_token is None:
		return Response({'status': 'Failure', 'message': 'Could not generate token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	

	print(payload)
	print(access_token)
	return Response({
		'status': 'Success',
		'username': user.username,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'token': access_token
	}, status=status.HTTP_200_OK)

#==================ยังไม่ใช้ใน Version==================
# @api_view(['POST', 'GET'])
# def Api_GetOTP(request, cmd):
# 	email = request.data.get('email', None)

# 	if not email:
# 		return Response({'status': 'Failure', 'message': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)

# 	if not CheckEmailValidate(email):
# 		return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

# 	if not User.objects.filter(username=email).exists():
# 		return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

# 	check = OTP.objects.filter(email=email)
# 	if check.count() >= 5:
# 		return Response({"error": "Maximum OTP requests reached. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
# 	if check.exists():
# 		last_otp = check.last()
# 		if last_otp.resend_at > timezone.now():
# 			return Response({"error": "OTP already sent. Please wait before requesting a new one."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

# 	try:
# 		from_email = ''
# 		otp = OTP.objects.create(email=email)
# 		subject = "Your OTP Code for resetting your password"
# 		message = f"Your OTP code is: {otp.code}"
# 		send_mail_obj = EmailMessage(subject, message, from_email, [email])
# 		threaded_send_to_email(send_mail_obj)
# 		return Response({'status': 'Success', 'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
# 	except Exception as e:
# 		print(f"Error sending OTP email: {str(e)}")
# 		return Response({"error": "Failed to send OTP email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['POST'])
# def Api_ResetPassword(request, cmd):
# 	email = request.data.get('email', None)
# 	otp_code = request.data.get('otp_code', None)
# 	old_password = request.data.get('old_password', None)
# 	new_password = request.data.get('new_password', None)

# 	if not email or not otp_code or not new_password:
# 		return Response({'status': 'Failure', 'message': 'Email, OTP code, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
	
# 	try:
# 		otp_entry = OTP.objects.filter(email=email, code=otp_code).last()

# 		if otp_entry is None:
# 			latest = OTP.objects.filter(email=email).last()
# 			if latest:
# 				latest.attempt_count += 1
# 				if latest.attempt_count >= 5:
# 					latest.delete()
# 					return Response(
# 						{'status': 'Failure', 'message': 'Too many failed attempts. Please request a new OTP.'},
# 						status=status.HTTP_429_TOO_MANY_REQUESTS,
# 					)
# 				latest.save(update_fields=['attempt_count'])
# 			return Response({'status': 'Failure', 'message': 'Invalid or expired OTP code'}, status=status.HTTP_400_BAD_REQUEST)

# 		if otp_entry.expires_at < timezone.now():
# 			return Response({'status': 'Failure', 'message': 'Invalid or expired OTP code'}, status=status.HTTP_400_BAD_REQUEST)
			
# 		if not CheckEmailValidate(email):
# 			return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

# 		if not CheckPasswordValidate(new_password):
# 			return Response({"error": "Password must contain only English letters, numbers, and the allowed special characters (! @ # $ % ^ & * ( ) - _ + = ? . ,)."}, status=status.HTTP_400_BAD_REQUEST,)

# 		user = User.objects.filter(username=email).first()
# 		if user is None:
# 			return Response({'status': 'Failure', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# 		if old_password is not None and not user.check_password(old_password):
# 			return Response({'status': 'Failure', 'message': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)

# 		if user.check_password(new_password):
# 			return Response({'status': 'Failure', 'message': 'New password must differ from old password'}, status=status.HTTP_400_BAD_REQUEST)

# 		user.set_password(new_password)
# 		user.save()

# 		# ลบ OTP ทั้งหมดของ email นี้ทิ้ง ไม่ใช่แค่ตัวที่ใช้
# 		OTP.objects.filter(email=email).delete()

# 		return Response({'status': 'Success', 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
# 	except Exception as e:
# 		print(f"Error resetting password: {str(e)}")
# 		return Response({"error": "Failed to reset password."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST','GET'])
def Api_GetFarm(request, cmd):
	access_token = request.data.get('access_token', None)
	username = request.data.get('username', None)

	if not jwt_decode(access_token):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	user = ProfileUser.objects.filter(username__username=username).first()
	if not user:
		return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

	dt = []
	dt = ProfileFarm.objects.filter(token=user.token)
	# for farm in farmData:
	
	serializer = ProfileFarmSerializer(dt, many=True)
	return Response(serializer.data)


@api_view(['POST','GET'])
def Api_GetFarm(request, cmd):
	access_token = request.data.get('access_token', None)
	username = request.data.get('username', None)

	if not jwt_decode(access_token):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	user = ProfileUser.objects.filter(username__username=username).first()
	if not user:
		return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)

	dt = []
	farmDatas = ProfileFarm.objects.filter(token=user.token)
	for farmData in farmDatas:
		device = ProfileDevice.objects.filter(nameFarm__nameFarm=farmData.nameFarm)
		userapp = ProfileUserApp.objects.filter(nameFarm__nameFarm=farmData.nameFarm)

		dt.append({
			"farm": ProfileFarmSerializer(farmData).data,
			"device": ProfileDeviceSerializer(device, many=True).data,
			"userapp": ProfileUserAppSerializer(userapp, many=True).data,
		})

	return Response(dt)


@api_view(['POST','GET'])
def Api_NewFarm(request, cmd):
	access_token = request.data.get('access_token', None)
	username = request.data.get('username', None)

	if not jwt_decode(access_token):
		return Response(data=TempNetResponseMsg.NO_PERM, status=status.HTTP_401_UNAUTHORIZED)

	user = ProfileUser.objects.filter(username__username=username).first()
	if not user:
		return Response(data=TempNetResponseMsg.NO_USER, status=status.HTTP_404_NOT_FOUND)