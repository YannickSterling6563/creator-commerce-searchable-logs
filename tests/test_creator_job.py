import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from creator_job import CreatorOrder, ship_creator_order


class MemorySink:
    def __init__(self):
        self.events = []

    def ingest_log(self, event):
        self.events.append(event)
        return {"accepted": True}


def test_delivery_precedes_subscriber_update():
    sink = MemorySink()
    order = CreatorOrder("order-1", "creator-7", "subscriber-22", "asset-4", 2900)

    steps = ship_creator_order(order, sink)

    assert steps == ["asset_delivery", "subscriber_update", "content_processing"]
    assert sink.events[0]["context"]["asset_id"] == "asset-4"
    assert sink.events[1]["context"]["subscriber_id"] == "subscriber-22"
