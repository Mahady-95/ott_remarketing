from fastapi import APIRouter
from database import get_connection

router = APIRouter()


@router.get("/segments/{segment_name}")
def get_segment_users(segment_name: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if segment_name == "inactive_7_days":
        query = """
            SELECT *
            FROM users
            WHERE last_active_at <= NOW() - INTERVAL 7 DAY
        """

    elif segment_name == "inactive_30_days":
        query = """
            SELECT *
            FROM users
            WHERE last_active_at <= NOW() - INTERVAL 30 DAY
        """

    elif segment_name == "active_subscribers":
        query = """
            SELECT *
            FROM users
            WHERE subscription_status = 'active'
        """

    elif segment_name == "expired_subscribers":
        query = """
            SELECT *
            FROM users
            WHERE subscription_status = 'expired'
        """

    elif segment_name == "unfinished_watchers":
        query = """
            SELECT DISTINCT u.*
            FROM users u
            JOIN watch_history wh ON u.id = wh.user_id
            WHERE wh.watch_percentage < 80
        """

    elif segment_name == "thriller_lovers":
        query = """
            SELECT DISTINCT u.*
            FROM users u
            JOIN watch_history wh ON u.id = wh.user_id
            WHERE wh.genre = 'Thriller'
        """

    else:
        cursor.close()
        conn.close()
        return {"error": "Invalid segment name"}

    cursor.execute(query)
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "segment": segment_name,
        "total_users": len(users),
        "users": users
    }