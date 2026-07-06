from __future__ import annotations

import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from urllib.parse import urlparse

from .api import public_router, router as api_router
from .auth import auth_router, get_current_user
from .foundation import foundation_router, init_foundation_db
from .db import db_session, initialize_database
from .features import is_email_connector_enabled, is_shared_instance
from .models import FeaturesRead
from .router.config_store import load_env_file
from .seed import seed_canary_workspace, seed_demo_workspace
from .update import load_trusted_update_keys


APP_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_DIR / "static"
ICON_PATH = STATIC_DIR / "faberloom.ico"

# Entry point de la ventana desktop (pywebview) y del servidor local.
HOST = os.getenv("FABERLOOM_HOST", "127.0.0.1")
PORT = int(os.getenv("FABERLOOM_PORT", "8000"))
APP_URL = f"http://{HOST}:{PORT}/static/index.html"
HEALTH_URL = f"http://{HOST}:{PORT}/api/health"


def app_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/static/index.html"


def health_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/api/health"


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env_file()
    with db_session() as conn:
        initialize_database(conn)
        seed_demo_workspace(conn)
        seed_canary_workspace(conn)
    init_foundation_db()
    load_trusted_update_keys()
    yield


def _trusted_hosts() -> set[str | None]:
    """Return the set of hostnames allowed for mutating browser requests.

    Localhost is always trusted.  Add extra hosts via ``FABERLOOM_CSRF_HOSTS``
    (comma-separated hostnames) or a single ``FABERLOOM_PUBLIC_HOST``.
    """

    hosts: set[str | None] = {None, "localhost", "127.0.0.1"}
    if os.getenv("FABERLOOM_PUBLIC_HOST"):
        hosts.add(os.getenv("FABERLOOM_PUBLIC_HOST"))
    extra = os.getenv("FABERLOOM_CSRF_HOSTS", "")
    for host in extra.split(","):
        host = host.strip()
        if host:
            hosts.add(host)
    return hosts


class LocalhostCSRFMiddleware(BaseHTTPMiddleware):
    """Reject cross-origin mutating requests against the local API.

    The UI is served from http://127.0.0.1:<port> locally.  Browsers send an
    Origin header on cross-origin POST/PUT/PATCH/DELETE; if it is present and
    not in the trusted host list we block it.  Requests with no Origin (e.g.
    the test client or a same-origin fetch) are allowed so the local-first UX
    keeps working without a separate auth token.

    For VPS deployments, set ``FABERLOOM_PUBLIC_HOST`` (e.g.
    ``app.faberloom.ai``) or ``FABERLOOM_CSRF_HOSTS``.
    """

    def __init__(self, app, trusted_hosts: set[str | None] | None = None):
        super().__init__(app)
        self.trusted_hosts = trusted_hosts or _trusted_hosts()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin") or request.headers.get("referer") or ""
            if origin:
                parsed = urlparse(origin)
                if parsed.hostname not in self.trusted_hosts:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Cross-origin request rejected"},
                    )
        return await call_next(request)


def _read_version() -> str:
    version_file = APP_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI(title="FaberLoom", version=_read_version(), lifespan=lifespan)
    app.add_middleware(LocalhostCSRFMiddleware)
    app.include_router(public_router)
    app.include_router(auth_router, prefix="/api")
    # Foundation Beta (M07-M20): gestiona su propia auth por sesión (M08),
    # por eso no lleva la dependencia JWT global.
    app.include_router(foundation_router, prefix="/api")
    app.include_router(api_router, dependencies=[Depends(get_current_user)])

    @app.exception_handler(PermissionError)
    def permission_error_handler(request, exc):  # noqa: ARG001
        return JSONResponse(
            status_code=403,
            content={"detail": "Workspace seal verification failed"},
        )

    @app.get("/api/features", response_model=FeaturesRead)
    def features():
        return FeaturesRead(
            email_connector_enabled=is_email_connector_enabled(),
            shared_instance=is_shared_instance(),
        )

    @app.get("/", include_in_schema=False)
    def index():
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>FaberLoom SL0</title>
                <style>
                  body {
                    margin: 0;
                    min-height: 100vh;
                    display: grid;
                    place-items: center;
                    background: #F4F1ED;
                    color: #1F1E1C;
                    font-family: Geist, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                  }
                  main {
                    width: min(680px, calc(100vw - 48px));
                    border: 1px solid #D8D0C0;
                    border-radius: 12px;
                    background: #FFFFFF;
                    padding: 32px;
                    box-shadow: 0 18px 60px rgba(31, 30, 28, 0.08);
                  }
                  .eyebrow {
                    color: #C96442;
                    font: 12px/1.4 "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                  }
                  h1 {
                    margin: 10px 0 12px;
                    font-family: "EB Garamond", Georgia, serif;
                    font-style: italic;
                    font-size: 44px;
                    font-weight: 500;
                    letter-spacing: -0.01em;
                  }
                  p { color: #5A544C; line-height: 1.6; margin: 0; }
                  code {
                    font-family: "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    color: #5A6B7C;
                  }
                </style>
              </head>
              <body>
                <main>
                  <div class="eyebrow">FaberLoom &middot; FaberLoom</div>
                  <h1>SL0 skeleton is running.</h1>
                  <p>Local state is backed by SQLite. Check <code>/api/health</code> and <code>/api/workspaces</code>.</p>
                </main>
              </body>
            </html>
            """
        )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


app = create_app()


def _run_server(host: str = HOST, port: int = PORT) -> None:
    """Corre uvicorn en este proceso (se usa en un hilo daemon para el desktop)."""
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="warning")


def _wait_until_ready(url: str = HEALTH_URL, timeout: float = 20.0) -> bool:
    """Sondea /api/health hasta que el servidor responda o se agote el tiempo."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as resp:  # noqa: S310 (URL local fija)
                if resp.status == 200:
                    return True
        except (URLError, OSError):
            time.sleep(0.2)
    return False


def run_desktop(host: str = HOST, port: int = PORT) -> None:
    """Levanta el backend en un hilo y abre la ventana pywebview de FaberLoom."""
    import webview

    server = threading.Thread(target=_run_server, args=(host, port), daemon=True)
    server.start()

    resolved_health_url = health_url(host, port)
    resolved_app_url = app_url(host, port)
    _wait_until_ready(resolved_health_url)

    webview.create_window(
        "FaberLoom",
        resolved_app_url,
        width=1320,
        height=860,
        min_size=(1000, 640),
        background_color="#F4F1ED",
    )
    webview.start()


def main() -> None:
    run_desktop()


if __name__ == "__main__":
    main()
