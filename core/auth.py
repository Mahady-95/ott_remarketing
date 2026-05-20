from fastapi import Request
from fastapi.responses import RedirectResponse

def require_login(request: Request):

    admin_id = request.session.get("admin_id")

    if not admin_id:
        return RedirectResponse("/login-ui", status_code=303)

    return None