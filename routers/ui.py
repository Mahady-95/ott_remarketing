from fastapi import APIRouter
from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from database import get_connection
from firebase_service import send_push_notification

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
def home():
    return RedirectResponse(
        url="/login-ui",
        status_code=303
    )

from database import get_connection


@router.get("/dashboard-ui")
def dashboard_ui(request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("""
        SELECT COUNT(*) AS inactive_users
        FROM users
        WHERE last_active_at <= NOW() - INTERVAL 7 DAY
    """)
    inactive_users = cursor.fetchone()["inactive_users"]

    cursor.execute("SELECT COUNT(*) AS total_campaigns FROM campaigns")
    total_campaigns = cursor.fetchone()["total_campaigns"]

    cursor.execute("""
        SELECT COUNT(*) AS total_clicked
        FROM campaign_logs
        WHERE status = 'clicked'
    """)
    total_clicked = cursor.fetchone()["total_clicked"]

    cursor.execute("""
        SELECT id, title, target_segment, channel, status, created_at
        FROM campaigns
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_campaigns = cursor.fetchall()

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

    recent_logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "title": "OTT Re-marketing Dashboard",
            "total_users": total_users,
            "inactive_users": inactive_users,
            "total_campaigns": total_campaigns,
            "total_clicked": total_clicked,
            "recent_campaigns": recent_campaigns,
            "recent_logs": recent_logs
        }
    )

@router.get("/users-ui")
def users_ui(request: Request):
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

    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "title": "Users",
            "users": users
        }
    )

@router.get("/campaigns-ui")
def campaigns_ui(request: Request):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM campaigns
        ORDER BY id DESC
    """)

    campaigns = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="campaigns.html",
        context={
            "title": "Campaigns",
            "campaigns": campaigns
        }
    )


from fastapi import Form
from fastapi.responses import RedirectResponse

@router.get("/campaigns-create-ui")
def campaign_create_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="campaign_create.html",
        context={
            "title": "Create Campaign"
        }
    )


@router.post("/campaigns-create-ui")
def create_campaign_ui(
    title: str = Form(...),
    message: str = Form(...),
    target_segment: str = Form(...),
    channel: str = Form(...),
    status: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO campaigns
        (title, message, target_segment, channel, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (title, message, target_segment, channel, status))

    conn.commit()

    cursor.close()
    conn.close()

    return RedirectResponse(
        url="/campaigns-ui",
        status_code=303
    )

@router.get("/campaigns-ui/{campaign_id}")
def campaign_details_ui(request: Request, campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM campaigns
        WHERE id = %s
    """, (campaign_id,))
    campaign = cursor.fetchone()

    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM campaign_logs
        WHERE campaign_id = %s
        GROUP BY status
    """, (campaign_id,))
    status_summary = cursor.fetchall()

    cursor.execute("""
        SELECT 
            cl.id,
            u.name AS user_name,
            u.email,
            u.phone,
            cl.status,
            cl.sent_at,
            cl.clicked_at
        FROM campaign_logs cl
        JOIN users u ON cl.user_id = u.id
        WHERE cl.campaign_id = %s
        ORDER BY cl.id DESC
    """, (campaign_id,))
    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="campaign_details.html",
        context={
            "title": "Campaign Details",
            "campaign": campaign,
            "status_summary": status_summary,
            "logs": logs
        }
    )
@router.post("/campaigns-ui/{campaign_id}/target-segment")
def target_segment_ui(campaign_id: int):
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
        return RedirectResponse(url="/campaigns-ui", status_code=303)

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
        return RedirectResponse(url=f"/campaigns-ui/{campaign_id}", status_code=303)

    cursor.execute(user_query)
    users = cursor.fetchall()

    for user in users:
        cursor.execute("""
            SELECT id
            FROM campaign_logs
            WHERE campaign_id = %s AND user_id = %s
        """, (campaign_id, user["id"]))

        existing = cursor.fetchone()

        if existing is None:
            cursor.execute("""
                INSERT INTO campaign_logs
                (campaign_id, user_id, status)
                VALUES (%s, %s, 'pending')
            """, (campaign_id, user["id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return RedirectResponse(
        url=f"/campaigns-ui/{campaign_id}",
        status_code=303
    )

from firebase_service import send_push_notification


@router.post("/campaigns-ui/{campaign_id}/send")
def send_campaign_ui(campaign_id: int):
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
        return RedirectResponse(url="/campaigns-ui", status_code=303)

    cursor.execute("""
        SELECT 
            cl.id AS log_id,
            u.device_token
        FROM campaign_logs cl
        JOIN users u ON cl.user_id = u.id
        WHERE cl.campaign_id = %s
        AND cl.status = 'pending'
    """, (campaign_id,))

    logs = cursor.fetchall()

    for log in logs:
        try:
            if not log["device_token"]:
                raise Exception("Device token missing")

            send_push_notification(
                device_token=log["device_token"],
                title=campaign["title"],
                body=campaign["message"]
            )

            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'sent',
                    sent_at = NOW()
                WHERE id = %s
            """, (log["log_id"],))

        except Exception:
            cursor.execute("""
                UPDATE campaign_logs
                SET status = 'failed'
                WHERE id = %s
            """, (log["log_id"],))

    conn.commit()
    cursor.close()
    conn.close()

    return RedirectResponse(
        url=f"/campaigns-ui/{campaign_id}",
        status_code=303
    )
@router.post("/campaigns-ui/{campaign_id}/retry-failed")
def retry_failed_ui(campaign_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaign_logs
        SET status = 'pending'
        WHERE campaign_id = %s
        AND status = 'failed'
    """, (campaign_id,))

    conn.commit()

    cursor.close()
    conn.close()

    return RedirectResponse(
        url=f"/campaigns-ui/{campaign_id}",
        status_code=303
    )
@router.post("/campaigns-ui/{campaign_id}/delete")
def delete_campaign_ui(campaign_id: int):
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

    cursor.close()
    conn.close()

    return RedirectResponse(
        url="/campaigns-ui",
        status_code=303
    )

@router.post("/campaigns-ui/{campaign_id}/status")
def update_campaign_status_ui(
    campaign_id: int,
    status: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaigns
        SET status = %s
        WHERE id = %s
    """, (status, campaign_id))

    conn.commit()

    cursor.close()
    conn.close()

    return RedirectResponse(
        url=f"/campaigns-ui/{campaign_id}",
        status_code=303
    )

@router.get("/login-ui")
def login_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Admin Login"
        }
    )

@router.post("/login-ui")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM admins
        WHERE email = %s AND password = %s
    """, (email, password))

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin:
        return RedirectResponse(
            url="/dashboard-ui",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "title": "Admin Login",
            "error": "Invalid email or password"
        }
    )

@router.get("/logout-ui")
def logout_ui():
    return RedirectResponse(
        url="/login-ui",
        status_code=303
    )

@router.get("/users-ui/{user_id}")
def user_details_ui(request: Request, user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email, phone, subscription_status, last_active_at, created_at
        FROM users
        WHERE id = %s
    """, (user_id,))
    user = cursor.fetchone()

    cursor.execute("""
        SELECT id, content_id, content_title, genre, watch_percentage, last_watched_at
        FROM watch_history
        WHERE user_id = %s
        ORDER BY id DESC
    """, (user_id,))
    watch_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="user_details.html",
        context={
            "title": "User Details",
            "user": user,
            "watch_history": watch_history
        }
    )

@router.get("/campaign-logs-ui")
def campaign_logs_ui(request: Request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            cl.id,
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

    return templates.TemplateResponse(
        request=request,
        name="campaign_logs.html",
        context={
            "title": "Campaign Logs",
            "logs": logs
        }
    )