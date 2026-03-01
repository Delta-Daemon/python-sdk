# DeltaDaemon Python SDK

Production-quality async Python SDK for the [DeltaDaemon API](https://deltadaemon.com/docs/getting-started/overview) — historical NWS forecast accuracy data for US weather stations.

## Install

Create and activate a virtual environment, then install:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install deltadaemon
```

From source:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e ".[dev]"   # with pytest
```

## Quick start

```python
import asyncio
from deltadaemon import DeltaDaemonClient

async def main():
    async with DeltaDaemonClient(api_key="your-api-key") as client:
        health = await client.get_health()
        print(health.status)

        stations = await client.get_station_metadata()
        for s in stations[:5]:
            print(f"{s.station_id}: {s.city_name}")

        summary = await client.get_accuracy_summary(city="Los Angeles", days=90)
        print(summary)

asyncio.run(main())
```

## Authentication

- Health and station metadata: no auth
- Data and accuracy: `Authorization: Bearer <API_KEY>` or session cookie
- API keys: https://deltadaemon.com/signin

Create the client with an API key:

```python
client = DeltaDaemonClient(api_key=os.environ.get("DELTADAEMON_API_KEY"))
```

## Endpoint groups

| Group | Methods |
|-------|---------|
| Health / metadata | `get_health`, `get_station_metadata` |
| Data | `get_forecast_actual`, `get_forecasts`, `get_observations`, `get_hourly_comparison`, `get_hourly_snapshot`, `get_forecast_run_stats` |
| Accuracy | `get_accuracy_summary`, `get_accuracy_by_date`, `get_city_accuracy`, `get_station_accuracy`, `get_bias_correction`, `get_exceedance`, etc. |

## Error handling

```python
from deltadaemon import DeltaDaemonClient
from deltadaemon.errors import AuthenticationError, PaymentRequiredError

async with DeltaDaemonClient(api_key=key) as client:
    try:
        data = await client.get_accuracy_summary(city="LA", days=90)
    except AuthenticationError:
        print("Invalid API key")
    except PaymentRequiredError:
        print("Subscription past due or cancelled")
```

## Examples

See `examples/` for practical workflows:

- `compare_stations.py` — compare accuracy across cities
- `trading_bot_workflow.py` — run stats, bias correction, exceedance
- `poll_accuracy.py` — async polling loop

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```
