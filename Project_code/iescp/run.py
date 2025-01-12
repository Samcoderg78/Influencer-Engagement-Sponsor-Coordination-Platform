# iescp/run.py
from app import create_app, db
from app.utils.celery_worker import celery_init_app
from app.models import User, Campaign, AdRequest
from sqlalchemy import text

app = create_app()  # Only get the Flask app
celery = celery_init_app(app)  # Initialize Celery with the Flask app

@app.before_request
def enable_foreign_keys():
    if db.engine.url.drivername == 'sqlite':
        db.session.execute(text('PRAGMA foreign_keys=ON'))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Campaign': Campaign, 'AdRequest': AdRequest}

if __name__ == '__main__':
    app.run(debug=True)
