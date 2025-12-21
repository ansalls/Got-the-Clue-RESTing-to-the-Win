from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .engine import BaseEventHook, SimulationEvent, SimulationRound


@dataclass
class TimelineHook(BaseEventHook):
    events: List[Dict[str, object]]

    def handle(self, event: SimulationEvent, payload: Dict[str, object]) -> None:
        record = {"event": event.value, "payload": payload}
        if event == SimulationEvent.ROUND_COMPLETED:
            round_summary = payload.get("round")
            if isinstance(round_summary, SimulationRound):
                record["payload"] = {
                    "round": round_summary.number,
                    "round_winner": round_summary.round_winner.name,
                    "round_scores": payload.get("round_scores"),
                }
        self.events.append(record)
