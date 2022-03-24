from app import dailyFunc


# scheduler = BlockingScheduler()
# @scheduler.scheduled_job('cron', id='fetch_daily', day='*',hour='5', minute='0')

print("start update")
dailyFunc()
print("finish update")