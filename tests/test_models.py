from deltadaemon.models import ExternalIds, HealthResponse, StationMetadata


def test_health_response_validation() -> None:
    data = {
        "status": "healthy",
        "timestamp": "2025-02-28T12:00:00Z",
        "database": "connected",
        "version": "1.0.0",
    }
    resp = HealthResponse.model_validate(data)
    assert resp.status == "healthy"
    assert resp.database == "connected"
    assert resp.version == "1.0.0"


def test_station_metadata_validation() -> None:
    data = {
        "station_id": "KLAX",
        "city_name": "Los Angeles",
        "country": "US",
        "latitude": 33.9425,
        "longitude": -118.408,
        "timezone": "America/Los_Angeles",
        "climate_zone": "dry",
        "data_active": True,
        "aliases": ["LA"],
        "external_ids": {"icao": "KLAX", "iata": "LAX"},
    }
    station = StationMetadata.model_validate(data)
    assert station.station_id == "KLAX"
    assert station.latitude == 33.9425
    assert station.external_ids is not None
    assert station.external_ids.icao == "KLAX"
    assert "LA" in station.aliases


def test_station_metadata_minimal() -> None:
    data = {
        "station_id": "KJFK",
        "city_name": "New York",
        "country": "US",
        "latitude": 40.0,
        "longitude": -74.0,
        "timezone": "America/New_York",
        "climate_zone": "humid",
    }
    station = StationMetadata.model_validate(data)
    assert station.data_active is True
    assert station.aliases == []
    assert station.external_ids is None
