# Serqo Python SDK

Official Python client for the Serqo Search API. Requires Python 3.10 or later and uses only the standard library.

## Install

```sh
pip install serqo
```

## Quick start

```python
import os
from serqo import Serqo

client = Serqo(api_key=os.environ["SERQO_API_KEY"])
response = client.search({
    "q": "espresso machines",
    "engine": "google",
    "type": "web",
    "gl": "us",
    "hl": "en",
})

print(response["data"]["results"])
print("Request ID:", response["requestId"])
```

Keep the API key in a server-side environment variable. The client returns the full response envelope as dictionaries.

## Methods

- `search(query, idempotency_key=None)` sends `POST /v1/search`.
- `engines()` returns the supported engines and search types.
- `me()` returns account and API key identifiers.
- `health()` checks the product API without sending an API key.

Read results from `response["data"]["results"]`. For pagination, use `response["data"]["pagination"]["nextStart"]`. See the [shared API reference](API.md) for all search parameters, response fields, and pagination behavior.

## Errors and retries

API errors raise `SerqoError`. It exposes `status`, `code`, `request_id`, `retryable`, `retry_after_ms`, and `details`. Connection failures raise `ConnectionError`; timeout handling is provided by `urllib`. The SDK does not retry searches automatically. When retrying an uncertain request, reuse the same `idempotency_key` with the same query within 24 hours.
