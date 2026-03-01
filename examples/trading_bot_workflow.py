"""Example trading-bot workflow: fetch runs, accuracy, and bias correction."""

import asyncio
import os

from deltadaemon import DeltaDaemonClient
from deltadaemon.errors import AuthenticationError, PaymentRequiredError


async def main() -> None:
    api_key = os.environ.get("DELTADAEMON_API_KEY")
    if not api_key:
        print("Set DELTADAEMON_API_KEY for data endpoints")
        return

    async with DeltaDaemonClient(api_key=api_key) as client:
        try:
            run_stats = await client.get_forecast_run_stats(station_id="KLAX")
            print("Run stats (KLAX):", run_stats)

            freshness = await client.get_data_freshness()
            print("Data freshness:", freshness)

            bias = await client.get_bias_correction(
                station_id="KLAX", forecast_temp=75, days=90
            )
            print("Bias correction for 75°F forecast:", bias)

            exceedance = await client.get_exceedance(
                station_id="KLAX", thresholds="1,2,3,5", days=90
            )
            print("Exceedance rates:", exceedance)
        except AuthenticationError:
            print("Invalid API key")
        except PaymentRequiredError:
            print("Subscription past due or cancelled")


if __name__ == "__main__":
    asyncio.run(main())
