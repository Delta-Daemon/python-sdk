from typing import Any

from pydantic import BaseModel, Field


class ExternalIds(BaseModel):
    """External identifiers for a station."""

    icao: str | None = None
    iata: str | None = None


class StationMetadata(BaseModel):
    """Station metadata with coordinates, timezone, and climate zone."""

    station_id: str
    city_name: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    climate_zone: str
    data_active: bool = True
    aliases: list[str] = Field(default_factory=list)
    external_ids: ExternalIds | None = None


class ResponseMetadata(BaseModel):
    """Metadata included in API responses."""

    generated_at: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    days_analyzed: int | None = None
    total_records: int | None = None
    query_time_ms: int | None = None
    station_id: str | None = None
    endpoint: str | None = None


class HealthResponse(BaseModel):
    """API health check response."""

    status: str
    timestamp: str
    database: str
    version: str


class SuccessResponse(BaseModel):
    """Generic success response wrapper."""

    success: bool = True
    data: Any = None
    metadata: ResponseMetadata | None = None


class ErrorResponse(BaseModel):
    """API error response."""

    success: bool = False
    error: str
    metadata: ResponseMetadata | None = None
