from apscheduler.schedulers.background import BackgroundScheduler
from systemUpdater import modelsApi

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(modelsApi.delete_expired_otp, 'interval', seconds=10)
    scheduler.start()