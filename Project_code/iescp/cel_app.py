from app.utils.celery_worker import celery_init_app
from celery.schedules import crontab
from app import create_app
from app.utils import celery_task as tasks  # Import the tasks module

# Initialize Flask and Celery app
flask_app = create_app()
print(flask_app)
celery_app = celery_init_app(flask_app)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run monthly activity report 
    sender.add_periodic_task(
        crontab(minute='*'), tasks.monthly_activity_report.s()
    )
    
    # Run daily reminders
    sender.add_periodic_task(
        crontab(minute='*'), tasks.daily_reminders.s()
    )
    
