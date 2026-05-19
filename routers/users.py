from fastapi import APIRouter
from database import get_connection
from pydantic import BaseModel

router = APIRouter()


class SubscriptionUpdate(BaseModel):
    subscription_status: str


class DeviceTokenUpdate(BaseModel):
    device_token: str
class UserActivityUpdate(BaseModel):
    user_id: int

@router.get("/users")
def get_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email, phone, subscription_status, last_active_at, created_at
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total_users": len(users),
        "users": users
    }


@router.get("/users/{user_id}")
def get_user_details(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email, phone, subscription_status, last_active_at, created_at
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return {"error": "User not found"}

    return user


@router.put("/users/{user_id}/subscription")
def update_subscription(user_id: int, data: SubscriptionUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET subscription_status = %s
        WHERE id = %s
    """, (data.subscription_status, user_id))

    conn.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    conn.close()

    if affected_rows == 0:
        return {"error": "User not found"}

    return {
        "message": "Subscription status updated successfully",
        "user_id": user_id,
        "subscription_status": data.subscription_status
    }


@router.put("/users/{user_id}/device-token")
def update_device_token(user_id: int, data: DeviceTokenUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET device_token = %s
        WHERE id = %s
    """, (data.device_token, user_id))

    conn.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    conn.close()

    if affected_rows == 0:
        return {"error": "User not found"}

    return {
        "message": "Device token updated successfully",
        "user_id": user_id
    }
@router.get("/inactive-users/{days}")
def get_inactive_users(days: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT id, name, email, phone, subscription_status, last_active_at
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL %s DAY
    """

    cursor.execute(query, (days,))
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "days": days,
        "total_inactive_users": len(users),
        "users": users
    }
@router.post("/users/activity")
def update_user_activity(data: UserActivityUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE users
        SET last_active_at = NOW()
        WHERE id = %s
    """

    cursor.execute(query, (data.user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "User activity updated successfully",
        "user_id": data.user_id
    }