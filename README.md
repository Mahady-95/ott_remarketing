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
```

---

# Installation

## Clone Project

```bash
git clone https://github.com/Mahady-95/ott_remarketing.git
```

## Enter Project Folder

```bash
cd ott_remarketing
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

## Install Requirements

```bash
pip install -r requirements.txt
```

---

# Database Setup

Create MySQL database:

```sql
CREATE DATABASE chorki_remarketing;
```

Update database credentials in:

```text
database.py
```

Example:

```python
host="localhost"
user="root"
password="YOUR_PASSWORD"
database="chorki_remarketing"
```

---

# Run Server

```bash
uvicorn main:app --reload
```

Server URL:

```text
http://127.0.0.1:8000
```

---

# Admin Login

Email:
```
admin@chorki.com
```

Password:
```
123456
```

---

# UI Routes

| Route | Description |
|---|---|
| /login-ui | Admin login |
| /dashboard-ui | Dashboard |
| /users-ui | Users page |
| /campaigns-ui | Campaigns page |
| /campaigns-create-ui | Create campaign |
| /campaign-logs-ui | Campaign logs |

---

# Workflow

1. Login
2. Create campaign
3. Target segment users
4. Send campaign
5. Track logs
6. Retry failed users

---

# Scheduler

- Automatically detects inactive users
- Creates campaign logs every interval

---

# Future Improvements

- Password hashing
- Real Firebase push notifications
- Email/SMS integration
- Celery queue system
- Docker deployment
- React frontend