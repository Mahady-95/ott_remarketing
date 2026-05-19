from fastapi import FastAPI

from scheduler import start_scheduler

from routers.users import router as users_router
from routers.campaigns import router as campaigns_router
from routers.dashboard import router as dashboard_router
from routers.watch_history import router as watch_history_router
from routers.admin import router as admin_router
from routers.segments import router as segments_router

app = FastAPI(
    title="Chorki Re-marketing API",
    description="Basic OTT Re-marketing and Retention System",
    version="1.0.0"
)

start_scheduler()

app.include_router(users_router)
app.include_router(campaigns_router)
app.include_router(dashboard_router)
app.include_router(watch_history_router)
app.include_router(admin_router)
app.include_router(segments_router)


@app.get("/")
def home():
    return {
        "message": "Chorki Re-marketing API running successfully"
    }