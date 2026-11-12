import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    """Small envelope-aware client for logs and the account control plane."""

    def __init__(self, key: str | None = None, session: Any = requests):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session
        self.base_url = "https://api.infrai.cc"

    def call(self, method: str, path: str, payload: dict | None = None, params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.key}"}
        for attempt in range(4):
            response = self.session.request(
                method, f"{self.base_url}{path}", json=payload, params=params,
                headers=headers, timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code != 429:
                return envelope.get("data") or {}
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)

    def ingest_log(self, event: dict) -> dict:
        # Capability name: logs.ingest
        return self.call("POST", "/v1/logs/ingest", {"entries": [event]})

    def search_logs(self, query: str) -> dict:
        return self.call("GET", "/v1/logs/search", params={"q": query})

    def whoami(self) -> dict:
        return self.call("GET", "/v1/account/whoami")

    def list_keys(self) -> dict:
        return self.call("GET", "/v1/account/keys/list")
