from datetime import datetime
from modelsApi import delete_expired_otp


def main():
    deleted = delete_expired_otp()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] systemUpdater: ลบ OTP ที่หมดอายุแล้วทิ้ง {deleted} รายการ")


if __name__ == "__main__":
    main()
