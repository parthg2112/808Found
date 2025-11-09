from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import time

from app.core.config import TIMEZONE, SCHEDULE_HOUR, SCHEDULE_MINUTE
from app.data.fetching import update_all_data

def run_data_fetching_job():
    """Runs the data fetching job."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running data fetching job...")
    try:
        update_all_data()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data fetching job finished successfully.")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data fetching job failed: {e}")

def start_scheduler():
    """Starts the scheduler."""
    tz = pytz.timezone(TIMEZONE)
    scheduler = BackgroundScheduler(timezone=tz)
    
    # Schedule the job to run every weekday at the specified time
    trigger = CronTrigger(
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        day_of_week='mon-fri',
        timezone=tz
    )
    scheduler.add_job(
        run_data_fetching_job,
        trigger=trigger,
        id='daily_data_fetch',
        replace_existing=True
    )
    
    print(f"Scheduler started. The data fetching job will run every weekday at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} {TIMEZONE}.")
    
    scheduler.start()
