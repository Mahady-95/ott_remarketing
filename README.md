# Chorki OTT Re-marketing System

A basic OTT re-marketing and user retention platform inspired by real OTT marketing systems like Chorki, Hoichoi, Netflix, and Bioscope.

This system helps OTT platforms:

- Identify inactive users
- Create targeted campaigns
- Send push notifications
- Track campaign performance
- Monitor user engagement
- Re-target users based on watch behavior

Built using FastAPI + MySQL.

---

# Features

## Admin Dashboard

- Total users count
- Inactive users count
- Total campaigns
- Click analytics
- Recent campaigns
- Recent campaign logs

---

## User Management

- Users list UI
- User details page
- Watch history tracking
- Search users

---

## Campaign Management

- Create campaign
- Campaign details
- Campaign status update
- Delete campaign
- Search campaigns

---

## Re-marketing Features

### Supported Segments

- inactive_7_days
- inactive_30_days
- active_subscribers
- expired_subscribers
- unfinished_watchers
- thriller_lovers

### Campaign Actions

- Target segment users
- Send campaign
- Retry failed campaign
- Campaign logs tracking

---

## Campaign Logs

- Pending logs
- Sent logs
- Failed logs
- Clicked logs
- Search logs

---

## Authentication

- Admin login UI
- Session-based login protection
- Logout system

---

# Tech Stack

| Technology | Usage |
|---|---|
| Python | Backend |
| FastAPI | API framework |
| MySQL | Database |
| Jinja2 | Frontend templating |
| Bootstrap 5 | UI design |
| APScheduler | Background scheduler |
| Firebase Admin SDK | Push notification |
| Uvicorn | Server |

---

# Project Structure

```text
CMR_APP/
│
├── main.py
├── database.py
├── scheduler.py
├── firebase_service.py
├── requirements.txt
├── README.md
│
├── routers/
│   ├── users.py
│   ├── campaigns.py
│   ├── dashboard.py
│   ├── watch_history.py
│   ├── admin.py
│   ├── segments.py
│   └── ui.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── users.html
│   ├── user_details.html
│   ├── campaigns.html
│   ├── campaign_create.html
│   ├── campaign_details.html
│   └── campaign_logs.html
│
├── static/
│
└── venv/

# Installation
## Clone Project

- git clone https://github.com/YOUR_USERNAME/ott_remarketing.git

##Enter Project folder
- cd ott_remarketing

## Create Virtual Environment
- python -m venv venv

# Activate Virtual Environment
## Windows
- venv\Scripts\activate
## Linux/Mac
- source venv/bin/activate

## Install Requirements
- pip install -r requirements.txt

# Database Setup
## Create MySQL database:
- CREATE DATABASE chorki_remarketing;

## Update database credentials in:
- database.py

## Example:
- host="localhost"
user="root"
password="YOUR_PASSWORD"
database="chorki_remarketing"

## Run Server
- uvicorn main:app --reload

## Server URL:
- http://127.0.0.1:8000

# UI Routes

## | Route                | Description     |
| -------------------- | --------------- |
| /login-ui            | Admin login     |
| /dashboard-ui        | Dashboard       |
| /users-ui            | Users page      |
| /campaigns-ui        | Campaigns page  |
| /campaigns-create-ui | Create campaign |
| /campaign-logs-ui    | Campaign logs   |

## Main Re-marketing Workflow

- Admin logs in
- Create campaign
- Target segment users
- Generate campaign logs
- Send campaign
- Track sent/failed/clicked users
- Retry failed users

# Scheduler
## Background scheduler automatically:

- Finds inactive users
- Creates pending campaign logs
- Helps automate re-marketing workflow

# Search Features
## Search by:

- Name
- Email
- Phone

#Campaign Search

## Search by:

- Campaign title
- Segment
- Status

# Campaign Logs Search

## Search by:

- Campaign
- User
- Email
- Phone
- Status

# Current Status
## Completed
- Backend API
- Dashboard UI
- User management
- Campaign management
- Logs system
- Session login
- Search filters
- Scheduler
- Firebase integration structure

#Future Improvements

- Password hashing
- Real Firebase push integration
- Email marketing integration
- SMS integration
- Advanced analytics
- Celery queue system
- Docker deployment
- React frontend
- AI recommendation engine
- A/B testing
- Multi-admin support
- Campaign scheduling UI

# Author

- Developed for OTT re-marketing learning and experimentation.

- Inspired by real OTT retention systems like Netflix, and Hoichoi.