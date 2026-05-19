from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection
from firebase_service import send_push_notification

router = APIRouter()


class CampaignCreate(BaseModel):
    title: str
    message: str
    target_segment: str
    channel: str = "push"
    status: str = "active"


class CampaignStatusUpdate(BaseModel):
    status: str


@router.post("/campaigns")
def create_campaign(campaign: CampaignCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO campaigns 
        (title, message, target_segment, channel, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        campaign.title,
        campaign.message,
        campaign.target_segment,
        campaign.channel,
        campaign.status
    ))

    conn.commit()
    campaign_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {
        "message": "Campaign created successfully",
        "campaign_id": campaign_id
    }


@router.get("/campaigns")
def get_campaigns():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM campaigns ORDER BY id DESC")
    campaigns = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_campaigns": len(campaigns),
        "campaigns": campaigns
    }


@router.put("/campaigns/{campaign_id}/status")
def update_campaign_status(campaign_id: int, data: CampaignStatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaigns
        SET status = %s
        WHERE id = %s
    """, (data.status, campaign_id))

    conn.commit()
    affected_rows = cursor.rowcount

    cursor.close()
    conn.close()

    if affected_rows == 0:
        return {"error": "Campaign not found"}

    return {
        "message": "Campaign status updated successfully",
        "campaign_id": campaign_id,
        "new_status": data.status
    }


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM campaign_logs
        WHERE campaign_id = %s
    """, (campaign_id,))

    cursor.execute("""
        DELETE FROM campaigns
        WHERE id = %s
    """, (campaign_id,))

    conn.commit()
    deleted_rows = cursor.rowcount

    cursor.close()
    conn.close()

    if deleted_rows == 0:
        return {"error": "Campaign not found"}

    return {
        "message": "Campaign deleted successfully",
        "campaign_id": campaign_id
    }


@router.post("/campaigns/{campaign_id}/target-segment")
def target_campaign_segment(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, target_segment
        FROM campaigns
        WHERE id = %s
    """, (campaign_id,))

    campaign = cursor.fetchone()

    if campaign is None:
        cursor.close()
        conn.close()
        return {"error": "Campaign not found"}

    segment = campaign["target_segment"]

    if segment == "inactive_7_days":
        user_query = """
            SELECT id FROM users
            WHERE last_active_at <= NOW() - INTERVAL 7 DAY
        """
    elif segment == "inactive_30_days":
        user_query = """
            SELECT id FROM users
            WHERE last_active_at <= NOW() - INTERVAL 30 DAY
        """
    elif segment == "active_subscribers":
        user_query = """
            SELECT id FROM users
            WHERE subscription_status = 'active'
        """
    elif segment == "expired_subscribers":
        user_query = """
            SELECT id FROM users
            WHERE subscription_status = 'expired'
        """
    elif segment == "unfinished_watchers":
        user_query = """
            SELECT DISTINCT u.id
            FROM users u
            JOIN watch_history wh ON u.id = wh.user_id
            WHERE wh.watch_percentage < 80
        """
    elif segment == "thriller_lovers":
        user_query = """
            SELECT DISTINCT u.id
            FROM users u
            JOIN watch_history wh ON u.id = wh.user_id
            WHERE wh.genre = 'Thriller'
        """
    else:
        cursor.close()
        conn.close()
        return {
            "error": "Invalid target segment",
            "target_segment": segment
        }

    cursor.execute(user_query)
    users = cursor.fetchall()

    inserted_count = 0

    for user in users:
        cursor.execute("""
            SELECT id
            FROM campaign_logs
            WHERE campaign_id = %s AND user_id = %s
        """, (campaign_id, user["id"]))

        existing_log = cursor.fetchone()

        if existing_log is None:
            cursor.execute("""
                INSERT INTO campaign_logs
                (campaign_id, user_id, status)
                VALUES (%s, %s, 'pending')
            """, (campaign_id, user["id"]))

            inserted_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Campaign target segment processed successfully",
        "campaign_id": campaign_id,
        "target_segment": segment,
        "total_users_found": len(users),
        "new_logs_created": inserted_count
    }


@router.post("/campaigns/{campaign_id}/send")
def send_campaign(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, title, message
        FROM campaigns
        WHERE id = %s
    """, (campaign_id,))

    campaign = cursor.fetchone()

    if campaign is None:
        cursor.close()
        conn.close()
        return {"error": "Campaign not found"}

    cursor.execute("""
        SELECT 
            cl.id AS log_id,
            u.id AS user_id,
            u.name,
            u.device_token
        FROM campaign_logs cl
        JOIN users u ON cl.user_id = u.id
        WHERE cl.campaign_id = %s
        AND cl.status = 'pending'
    """, (campaign_id,))

    logs = cursor.fetchall()

    sent_count = 0
    failed_count = 0

    for log in logs:
        try:
            if log["device_token"] is None or log["device_token"] == "":
                raise Exception("Device token missing")

            send_push_notification(
                device_token=log["device_token"],
                title=campaign["title"],
                body=campaign["message"]
            )

            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'sent', sent_at = NOW()
                WHERE id = %s
            """, (log["log_id"],))

            sent_count += 1

        except Exception:
            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'failed'
                WHERE id = %s
            """, (log["log_id"],))

            failed_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Campaign sending completed",
        "campaign_id": campaign_id,
        "total_pending": len(logs),
        "sent": sent_count,
        "failed": failed_count
    }


@router.get("/campaign-logs")
def get_campaign_logs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            cl.id,
            cl.campaign_id,
            c.title AS campaign_title,
            u.name AS user_name,
            u.email,
            u.phone,
            cl.status,
            cl.sent_at,
            cl.clicked_at
        FROM campaign_logs cl
        JOIN campaigns c ON cl.campaign_id = c.id
        JOIN users u ON cl.user_id = u.id
        ORDER BY cl.id DESC
    """)

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_logs": len(logs),
        "logs": logs
    }


@router.put("/campaigns/{campaign_id}/retry-failed")
def retry_failed_campaign_logs(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaign_logs
        SET status = 'pending'
        WHERE campaign_id = %s
        AND status = 'failed'
    """, (campaign_id,))

    conn.commit()
    updated_rows = cursor.rowcount

    cursor.close()
    conn.close()

    return {
        "message": "Failed logs moved to pending",
        "campaign_id": campaign_id,
        "total_retry_ready": updated_rows
    }


@router.put("/campaign-logs/{log_id}/click")
def mark_campaign_click(log_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaign_logs
        SET status = 'clicked',
            clicked_at = NOW()
        WHERE id = %s
    """, (log_id,))

    conn.commit()
    affected_rows = cursor.rowcount

    cursor.close()
    conn.close()

    if affected_rows == 0:
        return {"error": "Campaign log not found"}

    return {
        "message": "Campaign click tracked successfully",
        "log_id": log_id
    }


@router.get("/campaigns/{campaign_id}/report")
def campaign_report(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, title, message, target_segment, channel, status, created_at
        FROM campaigns
        WHERE id = %s
    """, (campaign_id,))

    campaign = cursor.fetchone()

    if campaign is None:
        cursor.close()
        conn.close()
        return {"error": "Campaign not found"}

    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM campaign_logs
        WHERE campaign_id = %s
        GROUP BY status
    """, (campaign_id,))

    status_summary = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS total_targeted
        FROM campaign_logs
        WHERE campaign_id = %s
    """, (campaign_id,))

    total_targeted = cursor.fetchone()["total_targeted"]

    cursor.close()
    conn.close()

    return {
        "campaign": campaign,
        "total_targeted_users": total_targeted,
        "status_summary": status_summary
    }


@router.get("/campaigns/{campaign_id}/analytics")
def campaign_analytics(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM campaign_logs
        WHERE campaign_id = %s
    """, (campaign_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS sent
        FROM campaign_logs
        WHERE campaign_id = %s AND status = 'sent'
    """, (campaign_id,))
    sent = cursor.fetchone()["sent"]

    cursor.execute("""
        SELECT COUNT(*) AS failed
        FROM campaign_logs
        WHERE campaign_id = %s AND status = 'failed'
    """, (campaign_id,))
    failed = cursor.fetchone()["failed"]

    cursor.execute("""
        SELECT COUNT(*) AS clicked
        FROM campaign_logs
        WHERE campaign_id = %s AND status = 'clicked'
    """, (campaign_id,))
    clicked = cursor.fetchone()["clicked"]

    cursor.close()
    conn.close()

    sent_rate = 0
    failed_rate = 0
    click_rate = 0

    if total > 0:
        sent_rate = round((sent / total) * 100, 2)
        failed_rate = round((failed / total) * 100, 2)
        click_rate = round((clicked / total) * 100, 2)

    return {
        "campaign_id": campaign_id,
        "total_targeted": total,
        "sent": sent,
        "failed": failed,
        "clicked": clicked,
        "sent_rate_percent": sent_rate,
        "failed_rate_percent": failed_rate,
        "click_rate_percent": click_rate
    }