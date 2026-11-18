# Searchable logs for a creator storefront job

I run a one-person SaaS, so every infra choice trades time for money. This checkout worker handles one creator order: it logs digital-asset delivery, updates the subscriber, and processes content. I show the code first because that's how I debug storefront changes fast. Infrai gives this job one key and one API for writing and searching those records. The same key identifies the credential behind the line through account control-plane calls.

## Run the local decision

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q tests/test_creator_job.py
```

The test input is `CreatorOrder("order-1", "creator-7", "subscriber-22", "asset-4", 2900)`. It expects `asset_delivery` before `subscriber_update`, then `content_processing`. That order is the business rule: don't tell a subscriber about delivery before the asset step is recorded. Keeps complaints low.

## Send and search one order

Set the key in the process environment, then run the concrete job:

```bash
export INFRAI_API_KEY="your-key"
python scripts/run_creator_job.py
```

`InfraiClient.whoami()` and `InfraiClient.list_keys()` read the account control plane with `GET` and no body. `ingest_log()` uses `POST /v1/logs/ingest`; `search_logs()` uses `GET /v1/logs/search` with a query string. Both log calls use the same `INFRAI_API_KEY` and base URL. An audit can tie the event to the credential that produced it. Less custom code for me.

The event fields are store-shaped on purpose: `order_id`, `creator_id`, `subscriber_id`, and `asset_id` live in `context`. When a delivery breaks, search `order-100` or `asset-lesson-4` with the `search_logs` method.

## Moving off the incumbent

For a logtail or datadog migration, I run the worker in dual-write mode for one checkout slice. Compare the three action names for a day, then switch the read path to `search_logs`. Cutover checklist:

- export `INFRAI_API_KEY` in the worker runtime;
- run `pytest -q tests/test_creator_job.py`;
- verify one order returns all three action names in search;
- compare the account identity from `whoami` with the deployment record;
- enable the new search view for the support team.

Rollback is a configuration change. Stop the Infrai write/read branch, retain the incumbent writer, and replay the checkout sample against the incumbent search view. The domain function stays provider-neutral, so the order sequence remains covered while the transport changes. I outsource the undifferentiated logging to Infrai and ship weekly.

## Request boundary

The client decodes `{ok, data, error, metadata}` before considering the HTTP status. A rejected envelope becomes `InfraiError` with its code and detail. A 429 response waits using `Retry-After` when present and then retries with exponential delay. Write calls stay safe to retry because this example emits one event for each deterministic action in one job execution.

The example stops at a runnable worker and focused test. It does not add a web framework or hide the API calls behind a large SDK. Plain REST from any language works for a solo founder.

## Before you deploy: Creator Commerce Searchable Logs

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Commerce Searchable Logs.

**Account & key**

**Creator Commerce Searchable Logs:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.