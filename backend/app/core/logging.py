import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter for SentinelForge.
    Ensures machine-parseable log lines and scrubs any obvious secret keywords.
    """

    REDACTED_KEYS = {"password", "token", "secret", "authorization", "api_key", "access_key"}

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        if hasattr(record, "actor"):
            log_obj["actor"] = record.actor

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Sanitize any extra fields
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            clean_extra = {}
            for k, v in record.extra.items():
                if any(secret_term in k.lower() for secret_term in self.REDACTED_KEYS):
                    clean_extra[k] = "[REDACTED]"
                else:
                    clean_extra[k] = v
            log_obj["extra"] = clean_extra

        return json.dumps(log_obj)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("sentinelforge")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logging()
