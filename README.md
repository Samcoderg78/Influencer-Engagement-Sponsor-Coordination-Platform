# Influencer Engagement & Sponsor Coordination Platform

A full-stack web platform that connects sponsors with influencers. Sponsors create campaigns and send sponsorship requests, influencers browse and respond to them, and admins moderate accounts across the platform.

**Tech stack:** React · Flask · SQLAlchemy · REST APIs · JWT · Celery · Redis · Flask-Caching

---

## Features

### Three user roles
| Role | What they can do |
|---|---|
| **Admin** | Moderate accounts, oversee campaigns and platform activity |
| **Sponsor** | Create and manage campaigns, send sponsorship requests to influencers, message influencers |
| **Influencer** | Browse campaigns, receive and respond to sponsorship requests, message sponsors |

### Core functionality
- **Campaign management:** sponsors create and manage campaigns
- **Sponsorship requests:** request and response workflow between sponsors and influencers
- **Messaging:** communication between sponsors and influencers
- **Account moderation:** admin controls over user accounts
- **Secure, role-based access:** JWT authentication with role-based authorization
- **Background processing:** Celery workers with Redis for tasks that shouldn't block a request `[TODO: name the tasks, e.g. scheduled reminders, report exports]`
- **Caching:** Flask-Caching for faster responses on frequently requested data

---

## Architecture

```
React frontend  ──REST APIs (JSON + JWT)──►  Flask backend  ──SQLAlchemy──►  Database
                                                  │
                                                  ├── Redis (cache + Celery broker)
                                                  └── Celery workers (background tasks)
```

---

## Getting started

### Prerequisites
- Python 3.8+
- Node.js and npm
- Redis running locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

---

## API overview


| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/login` | Log in and receive a JWT | Public |
| GET | `/api/campaigns` | List campaigns | Authenticated |
| POST | `/api/campaigns` | Create a campaign | Sponsor |

---

## What I learned

- Designing role-based access control across three user types
- Building a REST API with JWT authentication and connecting it to a React frontend
- Moving slow work into Celery and Redis so requests stay fast
- Using caching to reduce repeated database queries

---

## Author

**Saurabh Yadav**: [GitHub](https://github.com/Samcoderg78) · [LinkedIn](https://linkedin.com/in/saurabh-yadav-6zd)
