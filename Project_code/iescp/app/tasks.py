from flask import Blueprint, jsonify, send_file
from .utils.celery_task import daily_reminders, monthly_activity_report, export_campaigns_to_csv
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Campaign
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/api/tasks/daily-reminders', methods=['POST'])
def trigger_daily_reminders():
    daily_reminders.delay()  # Call the task
    return jsonify({"message": "Daily reminders task triggered!"}), 200

@tasks_bp.route('/api/tasks/monthly-report', methods=['POST'])
def trigger_monthly_report():
    monthly_activity_report.delay()  # Call the task
    return jsonify({"message": "Monthly report task triggered!"}), 200


