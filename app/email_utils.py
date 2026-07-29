# Source:
# https://studygyaan.com/django/how-to-send-email-with-attachments-in-django

from django.core.mail import EmailMessage
import threading


def send_email_with_attachment(subject, message, from_email, recipient_list, attachment_path):

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach_file(attachment_path)
    email.send()


def threaded_send_to_email(email: EmailMessage):
	thread = threading.Thread(target=send_to_email, args=(email,))
	try:
		thread.start()
		return True
	except Exception as e:
		print(f"Error starting thread for sending email: {e}")
		return False


def send_to_email(email: EmailMessage):
	try:
		email.send(fail_silently=False)
		return True
	except Exception as e:
		print(f"Error sending email: {e}")
		return False
