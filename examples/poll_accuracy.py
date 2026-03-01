"""Poll accuracy and forecast data in an async loop."""

import asyncio
import os

from deltadaemon import DeltaDaemonClient


async def main() -> None:
    api_key = os.environ.get("DELTADAEMON_API_KEY")
    interval_seconds = 300

    async with DeltaDaemonClient(api_key=api_key) as client:
        health = await client.get_health()
        print(f"API {health.status}, version {health.version}")

        while True:
            try:
                summary = await client.get_accuracy_summary(
                    city="Los Angeles", days=7
                )
                if isinstance(summary, dict):
                    data = summary.get("data", summary)
                    print(f"LA 7-day accuracy: {data}")

                snapshot = await client.get_hourly_snapshot(
                    station_id="KLAX", lookback_hours=6
                )
                print(f"Hourly snapshot keys: {list(snapshot.keys())}")
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
