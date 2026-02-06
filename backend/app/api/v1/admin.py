"""Admin endpoints — config reload, re-index triggers."""

from __future__ import annotations

import structlog
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])
log = structlog.get_logger()


@router.post("/config/reload")
async def reload_config():
    settings = get_settings()
    settings.reload_yaml()
    log.info("config_reloaded")
    return {"status": "ok", "message": "YAML configuration reloaded"}
