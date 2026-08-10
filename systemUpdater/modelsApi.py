from datetime import date, datetime, timedelta
from django.utils import timezone
from app import models
from app import serializers


def key_expire():
    now = timezone.now()
    models.AccessKey.objects.filter(expired_at__lte=timezone.now(), is_used=False).delete()
    return

def delete_expired_otp():
    now = timezone.now()
    total_deleted = 0

    emails = models.OTP.objects.values_list('email', flat=True).distinct()

    for email in emails:
        last_otp = models.OTP.objects.filter(email=email).order_by('id').last()
        if last_otp and last_otp.delete_at < now:
            count, _ = models.OTP.objects.filter(email=email).delete()
            total_deleted += count

    if total_deleted > 0:
        print(f"Deleted {total_deleted} OTP entries (cleared as a batch per email).")
    return