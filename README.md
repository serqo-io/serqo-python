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

Keep the API key in a server-side environment variable. The client returns the full response envelope as dictionaries and uses only Python's standard library.

## Configure the client

```python
from serqo import Serqo

client = Serqo(
    api_key="your-api-key",
    base_url="https://api.serqo.io",
    timeout=30,
)
```

`base_url` and `timeout` are optional. The default timeout is 60 seconds. Do not expose the API key in browser code or commit it to source control.

## Methods

- `search(query, idempotency_key=None)` sends `POST /v1/search`.
- `engines()` returns the supported engines and search types.
- `me()` returns account and API key identifiers.
- `health()` checks the product API without sending an API key.

Read results from `response["data"]["results"]`. For pagination, use `response["data"]["pagination"]["nextStart"]`. See the [API reference](https://github.com/serqo-io/serqo-python/blob/main/API.md) for search parameters, response fields, and pagination behavior.

## Errors and retries

API errors raise `SerqoError`. It exposes `status`, `code`, `request_id`, `retryable`, `retry_after_ms`, and `details`:

```python
from serqo import SerqoError

try:
    response = client.search({"q": "coffee shops", "engine": "google", "type": "maps"})
except SerqoError as error:
    print(error.status, error.code, error.request_id)
```

Connection failures raise `ConnectionError`; request timeouts raise `TimeoutError`. The SDK does not retry searches automatically. When retrying an uncertain request, reuse the same `idempotency_key` with the same query within 24 hours.

## Publish a release

Releases are published from GitHub Actions using PyPI Trusted Publishing. Configure a pending publisher on PyPI for owner `serqo-io`, repository `serqo-python`, workflow `release.yml`, and environment `pypi`. Then push a tag matching the version in `pyproject.toml`, such as `v0.1.0`. The workflow builds and checks both distributions before publishing them. See the [PyPI publishing guide](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
