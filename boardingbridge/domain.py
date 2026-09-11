from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .engine import Engine, Entity

@dataclass
class Reading:
    name: str
    value: float
    unit: str
    quality: str = "good"
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "value": round(self.value, 4), "unit": self.unit, "quality": self.quality, "at": self.at}

class DomainController:
    """Domain-specific control plane for aircraft bridge alignment, cabin height matching and wind safety.

    The controller models the important equipment chain: bridge -> match -> interlock -> wind -> panel -> alarm -> record.
    It is intentionally deterministic so the project remains easy to run locally.
    """

    FEATURES = ["bridge","match","interlock","wind","panel","alarm","record"]
    PRIMARY_MEASURE = "dock_cycles"

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.readings: list[Reading] = []
        self.commands: list[dict[str, Any]] = []
        self.thresholds = {"warning": 75.0, "critical": 90.0, "recovery": 35.0}

    def ingest(self, name: str, value: float, unit: str = "unit", quality: str = "good") -> Reading:
        reading = Reading(name, float(value), unit, quality)
        self.readings.append(reading)
        if len(self.readings) > 5000: self.readings = self.readings[-5000:]
        self.engine.metrics.observe(name, reading.value)
        return reading

    def latest(self, name: str | None = None) -> Reading | None:
        values = [x for x in self.readings if name is None or x.name == name]
        return values[-1] if values else None

    def health(self) -> dict[str, Any]:
        bad = sum(x.quality != "good" for x in self.readings[-100:])
        return {"status": "degraded" if bad else "healthy", "features": list(self.FEATURES), "readings": len(self.readings), "bad_readings": bad}

    def safety_check(self, value: float, warning: float | None = None, critical: float | None = None) -> dict[str, Any]:
        warning = self.thresholds["warning"] if warning is None else float(warning)
        critical = self.thresholds["critical"] if critical is None else float(critical)
        level = "critical" if value >= critical else "warning" if value >= warning else "normal"
        action = "trip-and-alarm" if level == "critical" else "notify" if level == "warning" else "continue"
        return {"value": value, "level": level, "action": action, "safe": level == "normal"}

    def command(self, entity_id: str, action: str, actor: str = "operator", **parameters: Any) -> dict[str, Any]:
        entity = self.engine.get(entity_id)
        action = str(action).strip().lower()
        index = self.engine.STATES.index(entity.state)
        state = entity.state
        if action in {"start", "open", "extend", "align", "dispatch", "enable"}: state = self.engine.STATES[min(index + 1, len(self.engine.STATES)-1)]
        elif action in {"alarm", "trip", "stop", "block"}: state = self.engine.STATES[-1]
        elif action in {"reset", "close", "recover"}: state = self.engine.DEFAULT_STATE
        if state != entity.state: self.engine.transition(entity_id, state, actor, action)
        command = {"entity_id": entity_id, "action": action, "actor": actor, "parameters": parameters, "result_state": state, "at": datetime.now(timezone.utc).isoformat()}
        self.commands.append(command)
        return command

    def batch_cycle(self, entity_ids: Iterable[str], signal: float) -> dict[str, Any]:
        results=[]
        decision=self.safety_check(signal)
        for entity_id in entity_ids:
            entity=self.engine.get(entity_id)
            if decision["level"] == "critical": results.append(self.command(entity.id, "trip", "controller", signal=signal))
            else: results.append({"entity_id": entity.id, "action": "observe", "state": entity.state})
        return {"decision": decision, "results": results}

    def forecast(self, horizon: int = 6) -> list[dict[str, Any]]:
        values=[x.value for x in self.readings[-20:]] or [0.0]
        mean=sum(values)/len(values)
        slope=(values[-1]-values[0])/max(1,len(values)-1)
        return [{"step": i+1, "value": round(mean+slope*(i+1), 3), "measure": self.PRIMARY_MEASURE} for i in range(max(1,horizon))]

    def report(self) -> dict[str, Any]:
        values=[x.value for x in self.readings]
        return {"features": list(self.FEATURES), "commands": len(self.commands), "health": self.health(), "latest": self.latest().as_dict() if self.latest() else None, "mean": round(statistics.fmean(values),3) if values else 0.0, "stdev": round(statistics.pstdev(values),3) if len(values)>1 else 0.0, "forecast": self.forecast(3)}

    def reset(self) -> None:
        self.readings.clear()
        self.commands.clear()

    def export(self) -> list[dict[str, Any]]:
        return [x.as_dict() for x in self.readings]

    def calibration(self, offset: float = 0.0, scale: float = 1.0) -> dict[str, Any]:
        adjusted=[]
        for reading in self.readings[-100:]: adjusted.append({"name": reading.name, "raw": reading.value, "adjusted": round(reading.value*scale+offset, 4), "unit": reading.unit})
        return {"offset": offset, "scale": scale, "samples": adjusted}

