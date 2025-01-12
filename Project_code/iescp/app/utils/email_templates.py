import os
from jinja2 import Template
from datetime import datetime
import csv


def create_html_report(sponsor_name, campaign_details):
    # Load HTML template for the monthly report
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Activity Report</title>
        <style type="text/css">
            body { font-family: Arial, sans-serif; }
            .container { width: 100%; max-width: 800px; margin: auto; }
            .header { background-color: #4CAF50; padding: 10px; text-align: center; color: white; }
            .content { background-color: #ffffff; padding: 20px; }
            .footer { background-color: #333; padding: 10px; text-align: center; color: white; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Monthly Activity Report for {{ sponsor_name }}</h2>
            </div>
            <div class="content">
                <p>Dear {{ sponsor_name | upper }},</p>
                <p>Here is your activity report for the month:</p>

                <center><u><h3>Campaign Summary</h3></u></center>
                <table>
                    <tr>
                        <th>Campaign Name</th>
                        <th>Budget (USD)</th>
                    </tr>
                    {% for campaign in campaign_details %}
                    <tr>
                        <td>{{ campaign.name }}</td>
                        <td>${{ campaign.budget }}</td>
                    </tr>
                    {% endfor %}
                    <tr>
                        <th>Total Sales</th>
                        <th>Rs.{{ total_sales }}</th>
                    </tr>
                </table>
            </div>
            <div class="footer">
                <p>Thank you for your continued partnership.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Calculate total sales using object attributes
    total_sales = sum(campaign.budget for campaign in campaign_details)

    # Render the template with the sponsor's data
    html_report = Template(template).render(
        sponsor_name=sponsor_name, 
        campaign_details=campaign_details,
        total_sales=total_sales
    )
    return html_report



def create_html_reminder(username, pending_requests):
    # HTML template for the reminder
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reminder</title>
        <style type="text/css">
            body { font-family: Arial, sans-serif; }
            .container { width: 100%; max-width: 600px; margin: auto; }
            .header { background-color: #4CAF50; padding: 10px; text-align: center; color: white; }
            .content { background-color: #ffffff; padding: 20px; }
            .footer { background-color: #333; padding: 10px; text-align: center; color: white; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
            th { background-color: #4CAF50; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Ad Request Reminder</h2>
            </div>
            <div class="content">
                <p>Dear {{ username | capitalize }},</p>
                <p>You have pending ad requests that need your attention. Please review the details below:</p>
                <table>
                    <tr>
                        <th>Request ID</th>
                        <th>Campaign Name</th>
                        <th>Description</th>
                        <th>Budget</th>
                    </tr>
                    {% for request in pending_requests %}
                    <tr>
                        <td>{{ request['id'] }}</td>
                        <td>{{ request['campaign_name'] }}</td>
                        <td>{{ request['campaign_description'] }}</td>
                        <td>{{ request['budget'] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                <p>Thank you for staying engaged.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>Ad Management Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Render the template
    html_reminder = Template(template).render(username=username, pending_requests=pending_requests)
    return html_reminder


def export_campaigns_to_csv(campaigns, sponsor_id, base_dir='exports'):
    """
    Helper function to generate a CSV file for sponsor campaigns.
    """
    import os
    from datetime import datetime

    # Define the directory to store the CSV files
    csv_dir = os.path.abspath(base_dir)
    os.makedirs(csv_dir, exist_ok=True)

    # Define the CSV file path
    csv_filename = f"campaigns_export_{sponsor_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    csv_path = os.path.join(csv_dir, csv_filename)

    # Write data to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Name', 'Description', 'Start Date', 'End Date', 'Budget', 'Visibility', 'Status', 'Goals']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for campaign in campaigns:
            writer.writerow({
                'ID': campaign.id,
                'Name': campaign.name,
                'Description': campaign.description,
                'Start Date': campaign.start_date.strftime('%Y-%m-%d'),
                'End Date': campaign.end_date.strftime('%Y-%m-%d'),
                'Budget': campaign.budget,
                'Visibility': campaign.visibility,
                'Status': campaign.status,
                'Goals': campaign.goals
            })
    return csv_path
