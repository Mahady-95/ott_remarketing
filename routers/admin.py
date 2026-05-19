from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection

router = APIRouter()


class AdminLogin(BaseModel):
    email: str
    password: str


@router.post("/admin/login")
def admin_login(data: AdminLogin):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email
        FROM admins
        WHERE email = %s AND password = %s
    """, (data.email, data.password))

    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    if admin is None:
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    return {
        "success": True,
        "message": "Login successful",
        "admin": admin
    }