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