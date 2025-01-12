# celery_task.py
from celery import shared_task
from datetime import datetime
from .email_templates import create_html_reminder, create_html_report, export_campaigns_to_csv
from .mail_hog import send_email
#from .csv_export import export_campaigns_to_csv
import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@shared_task(ignore_result=True)
def daily_reminders():
    """
    Scheduled Job - Daily reminders for influencers with pending ad requests.
    """
    from app.models import User, AdRequest
    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        logging.info(f"Daily reminders task started at {current_date}")
        
        influencers = User.query.filter_by(role='influencer').all()
        logging.info(f"Fetched {len(influencers)} influencers")

        for influencer in influencers:
            # Fetch pending requests
            pending_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status='Pending').all()
            logging.info(f"{influencer.username} has {len(pending_requests)} pending requests")

            if pending_requests:
                # Prepare reminder data
                reminder_data = [
                    {
                        "id": request.id,
                        "campaign_name": request.campaign.name,
                        "campaign_description": request.campaign.description,
                        "budget": request.budget
                    }
                    for request in pending_requests
                ]

                logging.debug(f"Reminder data generated for {influencer.username}: {reminder_data}")

                # Generate HTML content
                html_reminder = create_html_reminder(influencer.username, reminder_data)
                logging.info(f"HTML reminder created for {influencer.username}")

                # Send email
                send_email(influencer.email, 'Daily Reminder: Pending Ad Requests', html_reminder)
                logging.info(f"Reminder email sent to {influencer.email}")

    except Exception as e:
        logging.error(f"Error in daily_reminders task: {e}")

                
@shared_task(ignore_result=True)
def monthly_activity_report():
    """
    Scheduled Job - Monthly Activity Report for Sponsors.
    Compiles campaign activity details, including growth metrics and budget, and emails the
    report on the first day of every month.
    """
    from app.models import User, Campaign  # Importing here to avoid circular import
    
    sponsors = User.query.filter_by(role='sponsor').all()
    
    for sponsor in sponsors:
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
        
        # Generate the monthly activity report with campaign metrics
        html_report = create_html_report(sponsor, campaigns)
        
        # Send the report via email
        send_email(sponsor.email, 'Monthly Activity Report', html_report)
        print(f'Monthly Activity Report sent to {sponsor.username}')

@shared_task(ignore_result=True)
def export_campaigns_csv(sponsor_id):
    """
    User-Triggered Async Job - Export Campaign Details to CSV for Sponsors.
    Exports campaign details for public/private campaigns created by a sponsor and
    sends an alert once the CSV export is completed.
    """
    from app.models import User, Campaign
    try:
        # Fetch sponsor's campaigns
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()

        if not campaigns:
            print(f"No campaigns found for sponsor ID {sponsor_id}.")
            return

        # Generate the CSV file
        csv_path = export_campaigns_to_csv(campaigns, sponsor_id)

        # Fetch sponsor's details
        sponsor = User.query.get(sponsor_id)
        if not sponsor:
            print(f"Sponsor with ID {sponsor_id} not found.")
            return

        # Send alert email with the CSV file link (assuming `send_email` is implemented)
        email_subject = 'Campaign Data Export Completed'
        email_body = f'Dear {sponsor.username},\n\nYour campaign data has been successfully exported.\n\nYou can find the CSV file here: {csv_path}\n\nBest regards,\nYour Team'
        send_email(sponsor.email, email_subject, email_body)

        print(f'CSV export completed and notification sent to {sponsor.username}.')

    except Exception as e:
        print(f"Error during CSV export: {e}")
        # Log the exception (assumes logging is configured)
        import logging
        logging.error(f"Error during CSV export for sponsor ID {sponsor_id}: {e}")

