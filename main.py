from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

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

# templates = Jinja2Templates(directory="templates")

# app.mount("/static", StaticFiles(directory="static"), name="static")

from routers.ui import router as ui_router

app.include_router(ui_router)
