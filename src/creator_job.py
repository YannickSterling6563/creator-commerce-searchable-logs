from dataclasses import dataclass
from infrai_client import InfraiClient


class EventSink:
    def ingest_log(self, event: dict) -> dict:
        raise NotImplementedError


@dataclass(frozen=True)
class CreatorOrder:
    order_id: str
    creator_id: str
    subscriber_id: str
    asset_id: str
    total_cents: int


def ship_creator_order(order: CreatorOrder, sink: EventSink) -> list[str]:
    """Process delivery before the subscriber update, returning visible steps."""
    steps: list[str] = []
    events = [
        ("asset_delivery", {"asset_id": order.asset_id, "order_id": order.order_id}),
        ("subscriber_update", {"subscriber_id": order.subscriber_id, "order_id": order.order_id}),
        ("content_processing", {"creator_id": order.creator_id, "asset_id": order.asset_id}),
    ]
    for action, details in events:
        sink.ingest_log({
            "message": action,
            "level": "info",
            "context": {"service": "creator-commerce", "action": action, **details},
        })
        steps.append(action)
    return steps


def run(order: CreatorOrder, client: InfraiClient) -> dict:
    account = client.whoami()
    steps = ship_creator_order(order, client)
    return {"account": account, "order_id": order.order_id, "steps": steps}
