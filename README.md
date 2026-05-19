# OTT Re-marketing System

A basic OTT re-marketing and retention backend system built with FastAPI, MySQL, Firebase Cloud Messaging, and APScheduler.

## Features

- User management
- Watch history tracking
- Campaign creation
- Dynamic user segmentation
- Inactive user targeting
- Continue watching campaign
- Genre-based targeting
- Firebase push notification integration
- Campaign logs
- Click tracking
- Retry failed campaigns
- Dashboard summary APIs
- Auto scheduler for campaign processing

## Tech Stack

- Python
- FastAPI
- MySQL
- MySQL Workbench
- Firebase Cloud Messaging
- APScheduler
- python-dotenv

## Project Structure

```text
CMR_APP/
├── main.py
├── database.py
├── firebase_service.py
├── scheduler.py
├── requirements.txt
├── routers/
│   ├── users.py
│   ├── campaigns.py
│   ├── dashboard.py
│   ├── watch_history.py
│   ├── admin.py
│   └── segments.py