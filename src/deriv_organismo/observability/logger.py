from __future__ import annotations

import logging
from typing import Any


class AuditLogger:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("deriv_organismo.audit")

    def log_event(self, event: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("audit_event", extra=event)
        return event
