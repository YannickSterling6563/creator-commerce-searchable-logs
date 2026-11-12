import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from creator_job import CreatorOrder, run
from infrai_client import InfraiClient


if __name__ == "__main__":
    result = run(
        CreatorOrder("order-demo-100", "creator-7", "subscriber-22", "asset-lesson-4", 2900),
        InfraiClient(),
    )
    print(result)
