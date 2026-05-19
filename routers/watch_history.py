from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection

router = APIRouter()


class WatchHistoryCreate(BaseModel):
    user_id: int
    content_id: int
    content_title: str
    genre: str
    watch_percentage: int


@router.post("/watch-history")
def create_watch_history(data: WatchHistoryCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO watch_history
        (user_id, content_id, content_title, genre, watch_percentage, last_watched_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (
        data.user_id,
        data.content_id,
        data.content_title,
        data.genre,
        data.watch_percentage
    ))

    cursor.execute("""
        UPDATE users
        SET last_active_at = NOW()
        WHERE id = %s
    """, (data.user_id,))

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Watch history saved successfully",
        "user_id": data.user_id,
        "content_title": data.content_title
    }


@router.get("/watch-history")
def get_all_watch_history():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            wh.id,
            u.name AS user_name,
            wh.content_id,
            wh.content_title,
            wh.genre,
            wh.watch_percentage,
            wh.last_watched_at
        FROM watch_history wh
        JOIN users u ON wh.user_id = u.id
        ORDER BY wh.id DESC
    """)

    histories = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "total": len(histories),
        "watch_history": histories
    }


@router.get("/users/{user_id}/watch-history")
def get_user_watch_history(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, content_id, content_title, genre, watch_percentage, last_watched_at
        FROM watch_history
        WHERE user_id = %s
        ORDER BY id DESC
    """, (user_id,))

    histories = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "user_id": user_id,
        "total": len(histories),
        "watch_history": histories
    }