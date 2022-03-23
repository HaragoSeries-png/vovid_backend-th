from app import dailyFunc
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
@scheduler.scheduled_job('cron', id='fetch_daily', day='*',hour='5', minute='0')
def update_func():
    print("start update")
    # dailyFunc()
    print("finish update")