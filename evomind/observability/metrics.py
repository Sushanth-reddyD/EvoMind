"""Metrics collection using OpenTelemetry concepts."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Metrics collector for agent operations.
    
    Implements RED (Rate, Errors, Duration) metrics pattern.
    In production: export to Prometheus/OpenTelemetry.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[str, int] = defaultdict(int)
        self._histograms: Dict[str, list] = defaultdict(list)
        self._gauges: Dict[str, float] = {}

    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment counter metric."""
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record histogram value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set gauge value."""
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value

    def record_request(self, status: str, duration_ms: float) -> None:
        """Record request metrics (RED pattern)."""
        self.increment_counter("requests_total", labels={"status": status})
        self.record_histogram("request_duration_ms", duration_ms, labels={"status": status})

        if status == "error":
            self.increment_counter("errors_total")

    def record_tool_creation(self, success: bool, duration_ms: float) -> None:
        """Record tool creation metrics."""
        status = "success" if success else "failure"
        self.increment_counter("tool_creations_total", labels={"status": status})
        self.record_histogram("tool_creation_duration_ms", duration_ms)

    def record_execution(self, tool_id: str, success: bool, duration_ms: float) -> None:
        """Record execution metrics."""
        status = "success" if success else "failure"
        self.increment_counter("executions_total", labels={"tool": tool_id, "status": status})
        self.record_histogram("execution_duration_ms", duration_ms, labels={"tool": tool_id})

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics snapshot."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "histograms": {k: self._summarize_histogram(v) for k, v in self._histograms.items()},
                "gauges": dict(self._gauges),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _summarize_histogram(self, values: list) -> Dict[str, float]:
        """Summarize histogram values."""
        if not values:
            return {"count": 0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "sum": sum(sorted_values),
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p50": sorted_values[int(count * 0.5)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)] if count > 100 else sorted_values[-1]
        }

    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Create metric key with labels."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()
            self._gauges.clear()


# Global metrics collector instance
_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _metrics
