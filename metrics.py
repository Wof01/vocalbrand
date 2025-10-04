"""Lightweight performance metrics collection for VocalBrand."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any

@dataclass
class MetricRecord:
    name: str
    elapsed: float
    success: bool
    extra: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    def __init__(self):
        self.records: List[MetricRecord] = []

    def timing(self, name: str):
        def wrapper(func: Callable):
            def inner(*args, **kwargs):
                start = time.perf_counter()
                success = True
                extra: Dict[str, Any] = {}
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:  # noqa: BLE001
                    success = False
                    extra['error'] = str(e)
                    raise
                finally:
                    elapsed = time.perf_counter() - start
                    self.records.append(MetricRecord(name=name, elapsed=elapsed, success=success, extra=extra))
            return inner
        return wrapper

    def summary(self) -> Dict[str, Any]:
        if not self.records:
            return {"count": 0}
        total = len(self.records)
        avg = sum(r.elapsed for r in self.records) / total
        failures = sum(1 for r in self.records if not r.success)
        return {"count": total, "avg_sec": round(avg,3), "failures": failures}

metrics_collector = MetricsCollector()
