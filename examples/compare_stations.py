"""Compare forecast accuracy across multiple stations or cities."""

import asyncio
import os

from deltadaemon import DeltaDaemonClient


async def main() -> None:
    api_key = os.environ.get("DELTADAEMON_API_KEY")
    if not api_key:
        print("Set DELTADAEMON_API_KEY")
        return
    async with DeltaDaemonClient(api_key=api_key) as client:
        acc = await client.get_city_accuracy(
            days=90, min_samples=100, sort_by="mae"
        )
        if isinstance(acc, dict):
            data = acc.get("data", acc)
            if isinstance(data, list):
                for row in data[:10]:
                    stats = row.get("stats") or {}
                    mae = stats.get("mae")
                    n = row.get("sample_size") or stats.get("verification_pairs")
                    print(f"{row.get('city_name', 'N/A')}: MAE={mae}, n={n}")


if __name__ == "__main__":
    asyncio.run(main())
