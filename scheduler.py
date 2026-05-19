from apscheduler.schedulers.background import BackgroundScheduler
from database import get_connection
from firebase_service import send_push_notification


def auto_create_inactive_campaign_logs():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    campaign_id = 1
    days = 7

    inactive_query = """
        SELECT id
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL %s DAY
    """

    cursor.execute(inactive_query, (days,))
    users = cursor.fetchall()

    inserted_count = 0

    for user in users:
        check_query = """
            SELECT id
            FROM campaign_logs
            WHERE campaign_id = %s AND user_id = %s
        """
        cursor.execute(check_query, (campaign_id, user["id"]))
        existing_log = cursor.fetchone()

        if existing_log is None:
            insert_query = """
                INSERT INTO campaign_logs
                (campaign_id, user_id, status)
                VALUES (%s, %s, 'pending')
            """
            cursor.execute(insert_query, (campaign_id, user["id"]))
            inserted_count += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Auto inactive check completed. New logs created: {inserted_count}")


def auto_send_pending_campaigns():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            cl.id AS log_id,
            cl.campaign_id,
            c.title,
            c.message,
            u.device_token
        FROM campaign_logs cl
        JOIN campaigns c ON cl.campaign_id = c.id
        JOIN users u ON cl.user_id = u.id
        WHERE cl.status = 'pending'
    """

    cursor.execute(query)
    logs = cursor.fetchall()

    sent_count = 0
    failed_count = 0

    for log in logs:
        try:
            if log["device_token"] is None or log["device_token"] == "":
                raise Exception("Device token missing")

            send_push_notification(
                device_token=log["device_token"],
                title=log["title"],
                body=log["message"]
            )

            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'sent',
                    sent_at = NOW()
                WHERE id = %s
            """, (log["log_id"],))

            sent_count += 1

        except Exception as e:
            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'failed'
                WHERE id = %s
            """, (log["log_id"],))

            failed_count += 1

            print(f"Failed to send log_id {log['log_id']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Auto send completed. Sent={sent_count}, Failed={failed_count}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        auto_create_inactive_campaign_logs,
        "interval",
        minutes=1
    )

    scheduler.add_job(
        auto_send_pending_campaigns,
        "interval",
        minutes=1
    )

    scheduler.start()

    print("Scheduler started...")