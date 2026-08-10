from django.test import TestCase

# Create your tests here.
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


#--------------------------------------------------------------------------------------------------
	# token = request.data.get("captcha_token")
		
	# if not token:
	# 	return Response({"error": "Captcha token not found."}, status=400)

	# is_valid, error = verify_captcha(token, remote_ip=request.META.get("REMOTE_ADDR"))
	# if not is_valid:
	# 	return Response({"error": error}, status=403)