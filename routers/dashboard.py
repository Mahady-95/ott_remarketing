from fastapi import APIRouter
from database import get_connection

router = APIRouter()


@router.get("/dashboard/summary")
def dashboard_summary():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("""
        SELECT COUNT(*) AS inactive_7_days
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL 7 DAY
    """)
    inactive_7_days = cursor.fetchone()["inactive_7_days"]

    cursor.execute("SELECT COUNT(*) AS total_campaigns FROM campaigns")
    total_campaigns = cursor.fetchone()["total_campaigns"]

    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM campaign_logs
        GROUP BY status
    """)
    log_status = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_users": total_users,
        "inactive_7_days": inactive_7_days,
        "total_campaigns": total_campaigns,
        "campaign_log_status": log_status
    }


@router.get("/dashboard/recent-campaigns")
def recent_campaigns():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, title, target_segment, channel, status, created_at
        FROM campaigns
        ORDER BY id DESC
        LIMIT 5
    """)

    campaigns = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "recent_campaigns": campaigns
    }


@router.get("/dashboard/recent-logs")
def recent_logs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            cl.id,
            c.title AS campaign_title,
            u.name AS user_name,
            cl.status,
            cl.sent_at,
            cl.clicked_at
        FROM campaign_logs cl
        JOIN campaigns c ON cl.campaign_id = c.id
        JOIN users u ON cl.user_id = u.id
        ORDER BY cl.id DESC
        LIMIT 10
    """)

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "recent_logs": logs
    }


@router.get("/dashboard/segment-summary")
def segment_summary():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS inactive_7_days
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL 7 DAY
    """)
    inactive_7_days = cursor.fetchone()["inactive_7_days"]

    cursor.execute("""
        SELECT COUNT(*) AS inactive_30_days
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL 30 DAY
    """)
    inactive_30_days = cursor.fetchone()["inactive_30_days"]

    cursor.execute("""
        SELECT COUNT(*) AS active_subscribers
        FROM users
        WHERE subscription_status = 'active'
    """)
    active_subscribers = cursor.fetchone()["active_subscribers"]

    cursor.execute("""
        SELECT COUNT(*) AS expired_subscribers
        FROM users
        WHERE subscription_status = 'expired'
    """)
    expired_subscribers = cursor.fetchone()["expired_subscribers"]

    cursor.close()
    conn.close()

    return {
        "inactive_7_days": inactive_7_days,
        "inactive_30_days": inactive_30_days,
        "active_subscribers": active_subscribers,
        "expired_subscribers": expired_subscribers
    }