from datetime import date, datetime, timedelta
from app import models
from app import serializers

loop = 0

def print_loop():
    global loop
    loop += 1
    print()
    print("***************************************************")
    print("Call update_modelsApi")
    print('loop= {}'.format(loop))
    print('date/time= {}'.format(datetime.today()))
    print("***************************************************")



def delete_expired_otp():
    """ลบ OTP ที่หมดอายุแล้วทิ้งจากฐานข้อมูล คืนค่าจำนวนแถวที่ลบไป"""
    deleted_count, _ = models.OTP.objects.filter(expires_at__lt=datetime.now()).delete()
    return deleted_count
