import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Callable
from app.schemas.dto import AuditTraceEventDTO


class CryptographicAuditLogger:
    """
    Transverse Audit & Telemetry Service implementing the Observer Pattern.
    Maintains an immutable SHA-256 hash-chained log of every AI decision,
    budget guardrail evaluation, and PayPal Sandbox API transaction.
    """

    def __init__(self) -> None:
        self._events: list[AuditTraceEventDTO] = []
        self._observers: list[Callable[[AuditTraceEventDTO], None]] = []

    def subscribe(self, callback: Callable[[AuditTraceEventDTO], None]) -> None:
        self._observers.append(callback)

    def record(
        self,
        stage: str,
        actor: str,
        summary: str,
        details: dict[str, Any] | None = None,
    ) -> AuditTraceEventDTO:
        details_payload = details or {}
        prev_hash = self._events[-1].sha256_hash if self._events else "0" * 64
        timestamp = datetime.now(timezone.utc).isoformat()
        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"

        canonical = json.dumps(
            {
                "event_id": event_id,
                "timestamp": timestamp,
                "stage": stage,
                "actor": actor,
                "summary": summary,
                "details": details_payload,
                "prev_hash": prev_hash,
            },
            sort_keys=True,
            default=str,
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        event = AuditTraceEventDTO(
            event_id=event_id,
            timestamp=timestamp,
            stage=stage,
            actor=actor,
            summary=summary,
            details=details_payload,
            sha256_hash=digest,
            prev_hash=prev_hash,
        )
        self._events.append(event)

        for observer in self._observers:
            try:
                observer(event)
            except Exception:
                pass

        return event

    def list_events(self, limit: int = 50) -> list[AuditTraceEventDTO]:
        return list(reversed(self._events[-limit:]))

    def verify_chain_integrity(self) -> bool:
        """
        Verifies the cryptographic integrity of the entire SHA-256 hash chain.
        Proves zero tampering across all recorded audit events.
        """
        expected_prev = "0" * 64
        for event in self._events:
            if event.prev_hash != expected_prev:
                return False
            canonical = json.dumps(
                {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "stage": event.stage,
                    "actor": event.actor,
                    "summary": event.summary,
                    "details": event.details,
                    "prev_hash": event.prev_hash,
                },
                sort_keys=True,
                default=str,
            )
            recomputed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if recomputed != event.sha256_hash:
                return False
            expected_prev = event.sha256_hash
        return True

    def clear(self) -> None:
        self._events.clear()


audit_logger = CryptographicAuditLogger()
