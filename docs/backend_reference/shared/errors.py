from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class ErrorCode:
    # schema / parsing
    SCHEMA_PARSE_ERROR = "SCHEMA_PARSE_ERROR"
    SCHEMA_VALIDATION_ERROR = "SCHEMA_VALIDATION_ERROR"
    SCHEMA_REPAIR_FAILED = "SCHEMA_REPAIR_FAILED"

    # provider / transport
    PROVIDER_DISABLED = "PROVIDER_DISABLED"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_AUTH_ERROR = "PROVIDER_AUTH_ERROR"
    PROVIDER_RATE_LIMIT = "PROVIDER_RATE_LIMIT"
    PROVIDER_UPSTREAM_ERROR = "PROVIDER_UPSTREAM_ERROR"

    # internal / unknown
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class ClassifiedError:
    code: str
    message: str
    http_status: Optional[int] = None
    retry_after_s: Optional[float] = None


def classify_http_status(status: Optional[int], message: str, retry_after_s: Optional[float] = None) -> ClassifiedError:
    if status is None:
        return ClassifiedError(ErrorCode.UNKNOWN, message, None, retry_after_s)
    if status == 401 or status == 403:
        return ClassifiedError(ErrorCode.PROVIDER_AUTH_ERROR, message, status, retry_after_s)
    if status == 408:
        return ClassifiedError(ErrorCode.PROVIDER_TIMEOUT, message, status, retry_after_s)
    if status == 429:
        return ClassifiedError(ErrorCode.PROVIDER_RATE_LIMIT, message, status, retry_after_s)
    if 500 <= status < 600:
        return ClassifiedError(ErrorCode.PROVIDER_UPSTREAM_ERROR, message, status, retry_after_s)
    return ClassifiedError(ErrorCode.UNKNOWN, message, status, retry_after_s)
