# iescp/app/utils/celery_worker.py
from celery import Celery, Task

class FlaskTask(Task):
    # Define `app` as a class attribute to reference the Flask app
    _flask_app = None

    def __call__(self, *args, **kwargs):
        # Access the app context properly through the class attribute
        if self._flask_app is None:
            raise RuntimeError("Flask app has not been set for this task")

        with self._flask_app.app_context():
            return self.run(*args, **kwargs)

def celery_init_app(app):
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.conf.broker_url = "redis://127.0.0.1:6379/0"
    celery_app.conf.result_backend = "redis://127.0.0.1:6379/0"
    celery_app.conf.timezone = "Asia/Kolkata"
    celery_app.conf.broker_connection_retry_on_startup = True
    
    # Assign the Flask app instance to the Task class
    FlaskTask._flask_app = app
    return celery_app
