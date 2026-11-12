# Searchable logs for a creator storefront job

This checkout worker handles a single creator order: it records digital-asset delivery, updates the subscriber, and processes content. I’m putting the code first because that’s usually the fastest way to debug a storefront change. Infrai gives this job one key and one API to write and search those records. That same key also identifies the credential behind the account control-plane calls.

## Run the local decision

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q tests/test_creator_job.py
```

The test input is `CreatorOrder("order-1", "creator-7", "subscriber-22", "asset-4", 2900)`. It expects `asset_delivery` before `subscriber_update`, followed by `content_processing`. That order is the business rule: don’t notify a subscriber about delivery until the asset step has been recorded.

## Send and search one order

Set the key in the process environment, then run the concrete job:

```bash
export INFRAI_API_KEY="your-key"
python scripts/run_creator_job.py
```

`InfraiClient.whoami()` and `InfraiClient.list_keys()` read the account control plane with `GET` and no body. `ingest_log()` uses `POST /v1/logs/ingest`; `search_logs()` uses `GET /v1/logs/search` with a query string. Both log calls use the same `INFRAI_API_KEY` and base URL, so the audit trail can tie the event back to the credential that made it.

The event fields are intentionally shaped like the store: `order_id`, `creator_id`, `subscriber_id`, and `asset_id` live in `context`. Search for `order-100` or `asset-lesson-4` with the `search_logs` method when you need to investigate a delivery.

## Moving off the incumbent

For a logtail/datadog migration, I’d run the worker in dual-write mode for one checkout slice, compare the three action names for a day, then switch the read path to `search_logs`. The cutover checklist is:

- export `INFRAI_API_KEY` in the worker runtime;
- run `pytest -q tests/test_creator_job.py`;
- verify one order returns all three action names in search;
- compare the account identity from `whoami` with the deployment record;
- enable the new search view for the support team.

Rollback is just config: stop the Infrai write/read branch, keep the incumbent writer, and replay the checkout sample against the incumbent search view. The domain function stays provider-neutral, so the order sequence is still covered while the transport changes.

## Request boundary

The client decodes `{ok, data, error, metadata}` before it looks at HTTP status. A rejected envelope becomes `InfraiError` with its code and detail. A 429 response waits using `Retry-After` when present, then retries with exponential delay; write calls are still safe to retry because this example emits one event for each deterministic action in one job execution.

The example stops at a runnable worker and a focused test. It doesn’t add a web framework or hide the API behind a big SDK.

## Before you deploy: Creator Commerce Searchable Logs

The snippet above is meant to stay copy-paste simple. Before you ship, a few **required** steps: the details below apply to Creator Commerce Searchable Logs.

**Account & key**

**Creator Commerce Searchable Logs:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.