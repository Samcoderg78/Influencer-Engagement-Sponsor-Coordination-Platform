# Influencer Engagement & Sponsor Coordination Platform

A Flask-based web application for managing influencer campaigns, sponsorship requests, roles, messaging, and campaign administration. The system supports sponsors, influencers, admin moderation, and background task processing with Celery and Redis.

## Overview

This platform enables:

- Sponsors to create and manage public or private campaigns
- Influencers to browse campaign opportunities and respond to requests
- Admin review and approval of user accounts
- Messaging between sponsors and influencers
- CSV export of campaign data
- Background email/task processing using Celery

The project is implemented primarily in Python and uses a Flask app structure with SQLAlchemy, JWT authentication, Flask-Login, and a SQLite database by default.

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-JWT-Extended
- Flask-Migrate
- Flask-Caching
- Flask-Mail
- Celery
- Redis
- SQLite
- HTML templates
- Bootstrap-like frontend integration via templates

## Repository Structure

```text
Influencer-Engagement-Sponsor-Coordination-Platform/
├── Project_code/
│   └── iescp/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── forms.py
│       │   ├── models.py
│       │   ├── tasks.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── admin.py
│       │   │   ├── ad_requests.py
│       │   │   ├── auth.py
│       │   │   ├── campaigns.py
│       │   │   ├── influencer.py
│       │   │   ├── main.py
│       │   │   └── sponsor.py
│       │   ├── templates/
│       │   └── utils/
│       │       ├── celery_task.py
│       │       ├── celery_worker.py
│       │       ├── decorators.py
│       │       ├── email_templates.py
│       │       └── mail_hog.py
│       ├── config.py
│       ├── run.py
│       ├── req.txt
│       ├── migrations/
│       ├── exports/
│       ├── instance/
│       └── venv/
