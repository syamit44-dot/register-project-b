from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .jwt import jwt_encode
from .models import *
from .utilities import *
from .authentication import JWTAuthentication
import datetime 
 
class TempNetResponse:
	SUCCESS 	 = {'status': 'Success'}
	FAILURE 	 = {'status': 'Failure'}
	OK			 = {'status': 'OK'}
	 
@api_view(['POST'])
def Api_SignUp(request, cmd):
	username = request.data.get('username', None)
	password = request.data.get('password', None)

	if not username or not password:
		return Response({"error": "Please send username and password."}, status=status.HTTP_400_BAD_REQUEST)
	if not CheckEmailValidate(username):
		return Response({"error": "Username must be a valid email."}, status=status.HTTP_400_BAD_REQUEST)
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
			profile = ProfileUser.objects.create(
				username=user_core,
				first_name=user_core.first_name,
				last_name=user_core.last_name,
			)
	except Exception as e:
		print(f"Error creating user: {str(e)}")
		return Response({"error": "Failed to create user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	# ===== ส่วนที่เพิ่มเข้ามา: generate JWT ให้ user ทันทีหลัง signup =====
	now = timezone.now()
	payload = {
		'uid': user_core.id,
		'un': user_core.username,
		'exp': int((now + datetime.timedelta(hours=1)).timestamp()),
		'iat': int(now.timestamp()),
	}
	access_token = jwt_encode(payload)
	if access_token is None:
		return Response({"error": "User created but failed to generate token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({
		"message": "Created success.",
		"username": username,
		"token": access_token,
		"farm_token": str(profile.token),
	}, status=status.HTTP_201_CREATED)


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
		return Response({'status': 'Failure', 'message': 'Could not generate token'},
						 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	
	return Response({
		'status': 'Success',
		'username': user.username,
		'token': access_token,
		'farm_token': str(profile.token),
	}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def Api_SubmitData(request):
	data = request.data
	return Response({
		'status': 'Success',
		'received_from': request.user.username,
		'data': data,
	}, status=status.HTTP_200_OK)
# def Check_IpController():
# 	CHICKATRON20 	 = 'CKTRON20', 'Chickatron 20'
# 	CHICKATRON20N    = 'CKTRON-N', 'Chickatron 20 New'
# 	CHICKATRONLAYERS = 'CKTRON_L', 'Chickatron Layers'
# 	CHICKATRONBREEDERS= 'CKTRON_B', 'Chickatron Breeders'
# 	CHICKATRON13	 = 'CKTRON13', 'Chickatron 13'
# 	PIGATRON13		 = 'PIG13', 'Pigatron 13'
# 	T1200P		 	 = 'T1200+', 'Temp1200 Plus'
# 	RTRON 			 = 'T2004-PK', 'R-Tron'
# 	RTRON207		 = 'RTROn207', 'R-Tron 207'
# 	RTRON313		 = 'RTROn313', 'R-Tron 313'
# 	RTRON612		 = 'RTRON612', 'R-Tron 612'
# 	RTRON612P		 = 'RT612P', 'R-Tron 612 Pig'
# 	RTRON620		 = 'RTRON620', 'R-Tron 620'
# 	PTRON620P		 = 'RT620P', 'R-Tron 620 Pig'
# 	TP54S 			 = 'TP54S', 'TP54S'
# 	TP80 			 = 'TP80', 'TP80'
# 	TP82 			 = 'TP82', 'TP82'
# 	PUNO207 		 = 'PUNOS207', 'Punos 207'
# 	PUNO515 		 = 'PUNOS515', 'Punos 515'
# 	SILONICX         = 'SILO-X', 'Silonic X'
# 	SILONICXI        = 'SILO-XI', 'Silonic XI'
# 	OTHER            = 'OTHER', 'Other'


# @api_view(['POST'])
# def RegisterFarm(request):
# 	if request.method == 'POST':
# 		serializer = ProfileFarmSerializer(data=request.data)
		
# 		if serializer.is_valid():
# 			serializer.save() 
# 			return Response(
# 				data={"message": "Created new farm successfully!", "data": serializer.data}, 
# 				status=status.HTTP_201_CREATED
# 			)
# 		return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

