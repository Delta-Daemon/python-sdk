from unittest.mock import AsyncMock, MagicMock

import pytest

from deltadaemon import DeltaDaemonClient
from deltadaemon.errors import (
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
)


@pytest.fixture
def mock_transport() -> MagicMock:
    transport = MagicMock()
    transport.get = AsyncMock()
    transport.post = AsyncMock()
    transport.delete = AsyncMock()
    transport.__aenter__ = AsyncMock(return_value=transport)
    transport.__aexit__ = AsyncMock(return_value=None)
    return transport


@pytest.fixture
def client(mock_transport: MagicMock) -> DeltaDaemonClient:
    client = DeltaDaemonClient(api_key="test-key")
    client._transport = mock_transport
    return client


@pytest.mark.asyncio
async def test_get_health(client: DeltaDaemonClient, mock_transport: MagicMock) -> None:
    mock_transport.get.return_value = {
        "status": "healthy",
        "timestamp": "2025-02-28T12:00:00Z",
        "database": "connected",
        "version": "1.0.0",
    }
    result = await client.get_health()
    assert result.status == "healthy"
    assert result.database == "connected"
    mock_transport.get.assert_called_once_with("/api/v1/health")


@pytest.mark.asyncio
async def test_get_station_metadata(
    client: DeltaDaemonClient, mock_transport: MagicMock
) -> None:
    mock_transport.get.return_value = {
        "success": True,
        "data": [
            {
                "station_id": "KLAX",
                "city_name": "Los Angeles",
                "country": "US",
                "latitude": 33.9425,
                "longitude": -118.408,
                "timezone": "America/Los_Angeles",
                "climate_zone": "dry",
                "data_active": True,
                "aliases": [],
                "external_ids": {"icao": "KLAX", "iata": "LAX"},
            }
        ],
    }
    result = await client.get_station_metadata()
    assert len(result) == 1
    assert result[0].station_id == "KLAX"
    assert result[0].city_name == "Los Angeles"


@pytest.mark.asyncio
async def test_get_station_metadata_bare_data(
    client: DeltaDaemonClient, mock_transport: MagicMock
) -> None:
    mock_transport.get.return_value = [
        {
            "station_id": "KJFK",
            "city_name": "New York",
            "country": "US",
            "latitude": 40.6398,
            "longitude": -73.7789,
            "timezone": "America/New_York",
            "climate_zone": "humid",
            "data_active": True,
            "aliases": [],
        }
    ]
    result = await client.get_station_metadata()
    assert len(result) == 1
    assert result[0].station_id == "KJFK"


@pytest.mark.asyncio
async def test_get_accuracy_summary(
    client: DeltaDaemonClient, mock_transport: MagicMock
) -> None:
    mock_transport.get.return_value = {
        "success": True,
        "data": {"mae": 2.5, "bias": -0.3, "sample_count": 1000},
    }
    result = await client.get_accuracy_summary(city="Los Angeles", days=30)
    assert isinstance(result, dict)
    mock_transport.get.assert_called_once()
    call_args = mock_transport.get.call_args
    assert call_args[0][0] == "/api/v1/accuracy/summary"
    assert call_args[1]["params"]["city"] == "Los Angeles"
    assert call_args[1]["params"]["days"] == 30


@pytest.mark.asyncio
async def test_client_context_manager(mock_transport: MagicMock) -> None:
    mock_transport.get.return_value = {"status": "healthy", "timestamp": "", "database": "ok", "version": "1.0"}
    client = DeltaDaemonClient(api_key="key")
    client._transport = mock_transport
    async with client:
        await client.get_health()
    mock_transport.__aenter__.assert_called()
    mock_transport.__aexit__.assert_called()
