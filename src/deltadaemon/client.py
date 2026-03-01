from typing import Any, Literal

from deltadaemon._transport import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, Transport
from deltadaemon.models import HealthResponse, StationMetadata


SortBy = Literal["mae", "count", "mean_error", "city", "rmse"]
Format = Literal["json", "csv"]


class DeltaDaemonClient:
    """Async client for the DeltaDaemon API at api.deltadaemon.com."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._transport = Transport(
            base_url=base_url, api_key=api_key, timeout=timeout
        )

    async def __aenter__(self) -> "DeltaDaemonClient":
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self._transport.__aexit__(exc_type, exc_val, exc_tb)

    def _params(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        days: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        min_samples: int | None = None,
        sort_by: SortBy | None = None,
        format: Format | None = None,
        limit: int | None = None,
        include_raw: bool | None = None,
        reference_time: str | None = None,
        lookback_hours: int | None = None,
        forecast_for_date: str | None = None,
        forecast_temp: float | None = None,
        thresholds: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        plan: str | None = None,
        billing_period: str | None = None,
        months: int | None = None,
    ) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if station_id is not None:
            out["station_id"] = station_id
        if city is not None:
            out["city"] = city
        if days is not None:
            out["days"] = days
        if date_from is not None:
            out["date_from"] = date_from
        if date_to is not None:
            out["date_to"] = date_to
        if min_samples is not None:
            out["min_samples"] = min_samples
        if sort_by is not None:
            out["sort_by"] = sort_by
        if format is not None:
            out["format"] = format
        if limit is not None:
            out["limit"] = limit
        if include_raw is not None:
            out["include_raw"] = include_raw
        if reference_time is not None:
            out["reference_time"] = reference_time
        if lookback_hours is not None:
            out["lookback_hours"] = lookback_hours
        if forecast_for_date is not None:
            out["forecast_for_date"] = forecast_for_date
        if forecast_temp is not None:
            out["forecast_temp"] = forecast_temp
        if thresholds is not None:
            out["thresholds"] = thresholds
        if start_time is not None:
            out["start_time"] = start_time
        if end_time is not None:
            out["end_time"] = end_time
        if plan is not None:
            out["plan"] = plan
        if billing_period is not None:
            out["billing_period"] = billing_period
        if months is not None:
            out["months"] = months
        return out

    async def get_health(self) -> HealthResponse:
        """Health check. No authentication required."""
        data = await self._transport.get("/api/v1/health")
        return HealthResponse.model_validate(data)

    async def get_station_metadata(self) -> list[StationMetadata]:
        """All tracked stations with coordinates, timezone, climate zone. No auth required."""
        resp = await self._transport.get("/api/v1/stations/metadata")
        if isinstance(resp, str):
            raise ValueError("Expected JSON response")
        data = resp.get("data", resp) if isinstance(resp, dict) else resp
        if isinstance(data, list):
            return [StationMetadata.model_validate(item) for item in data]
        return [StationMetadata.model_validate(data)]

    async def signup(
        self, *, email: str, password: str, display_name: str | None = None
    ) -> dict[str, Any]:
        """Create account. Returns session info."""
        body: dict[str, Any] = {"email": email, "password": password}
        if display_name is not None:
            body["display_name"] = display_name
        return await self._transport.post("/auth/signup", body=body)

    async def login(self, *, email: str, password: str) -> dict[str, Any]:
        """Sign in. Sets session cookie if using browser; SDK returns response."""
        return await self._transport.post(
            "/auth/login", body={"email": email, "password": password}
        )

    async def forgot_password(self, *, email: str) -> dict[str, Any]:
        """Request password reset."""
        return await self._transport.post(
            "/auth/forgot-password", body={"email": email}
        )

    async def reset_password(
        self, *, token: str, password: str
    ) -> dict[str, Any]:
        """Reset password with token."""
        return await self._transport.post(
            "/auth/reset-password", body={"token": token, "password": password}
        )

    async def verify_email(self, *, token: str) -> dict[str, Any]:
        """Verify email with token."""
        return await self._transport.post(
            "/auth/verify-email", body={"token": token}
        )

    async def logout(self) -> dict[str, Any]:
        """Sign out."""
        return await self._transport.post("/auth/logout")

    async def get_me(self) -> dict[str, Any]:
        """Current user. Requires session cookie."""
        return await self._transport.get("/auth/me")

    async def get_usage(self) -> dict[str, Any]:
        """Usage stats for current period. Requires session cookie."""
        return await self._transport.get("/auth/usage")

    async def list_api_keys(self) -> dict[str, Any]:
        """List API key metadata. Requires session cookie."""
        return await self._transport.get("/api-keys")

    async def create_api_key(self, *, name: str | None = None) -> dict[str, Any]:
        """Create API key. Raw key returned once; store securely. Requires session."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return await self._transport.post("/api-keys", body=body)

    async def delete_api_key(self, key_id: str) -> dict[str, Any]:
        """Revoke API key. Requires session cookie."""
        return await self._transport.delete(f"/api-keys/{key_id}")

    async def create_checkout_session(
        self, *, plan: str, billing_period: str | None = None
    ) -> dict[str, Any]:
        """Create Stripe checkout session. Requires session cookie."""
        body: dict[str, Any] = {"plan": plan}
        if billing_period is not None:
            body["billing_period"] = billing_period
        return await self._transport.post(
            "/billing/create-checkout-session", body=body
        )

    async def create_btcpay_invoice(
        self, *, plan: str, months: int | None = None
    ) -> dict[str, Any]:
        """Create BTCPay invoice. Requires session cookie."""
        body: dict[str, Any] = {"plan": plan}
        if months is not None:
            body["months"] = months
        return await self._transport.post(
            "/billing/create-btcpay-invoice", body=body
        )

    async def get_subscription(self) -> dict[str, Any]:
        """Current subscription. Requires session cookie."""
        return await self._transport.get("/billing/subscription")

    async def get_forecast_actual(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 1000,
        format: Format = "json",
    ) -> dict[str, Any] | str:
        """Raw forecast-actual pairs. Requires API key or session."""
        params = self._params(
            station_id=station_id,
            city=city,
            days=days,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            format=format,
        )
        return await self._transport.get(
            "/api/v1/data/forecast-actual", params=params
        )

    async def get_forecasts(
        self,
        *,
        forecast_for_date: str,
        station_id: str | None = None,
        city: str | None = None,
        limit: int = 100,
        format: Format = "json",
    ) -> dict[str, Any] | str:
        """Forecast records for station and date. Requires API key or session."""
        params = self._params(
            forecast_for_date=forecast_for_date,
            station_id=station_id,
            city=city,
            limit=limit,
            format=format,
        )
        return await self._transport.get("/api/v1/data/forecasts", params=params)

    async def get_observations(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 1000,
        format: Format = "json",
    ) -> dict[str, Any] | str:
        """Raw station observations. Requires API key or session."""
        params = self._params(
            station_id=station_id,
            city=city,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            format=format,
        )
        return await self._transport.get(
            "/api/v1/data/observations", params=params
        )

    async def get_hourly_comparison(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        days: int = 7,
        lookback_hours: int = 0,
    ) -> dict[str, Any]:
        """Hourly forecast vs observation pairs. Requires API key or session."""
        params = self._params(
            station_id=station_id,
            city=city,
            days=days,
            lookback_hours=lookback_hours,
        )
        result = await self._transport.get(
            "/api/v1/data/hourly-comparison", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_hourly_snapshot(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        reference_time: str | None = None,
        lookback_hours: int = 6,
    ) -> dict[str, Any]:
        """Single NWS run hourly snapshot. Requires API key or session."""
        params = self._params(
            station_id=station_id,
            city=city,
            reference_time=reference_time,
            lookback_hours=lookback_hours,
        )
        result = await self._transport.get(
            "/api/v1/data/hourly-snapshot", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_forecast_run_stats(
        self,
        *,
        station_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """Forecast run frequency stats per station. Requires API key or session."""
        params = self._params(
            station_id=station_id,
            start_time=start_time,
            end_time=end_time,
        )
        result = await self._transport.get(
            "/api/v1/data/run-stats", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_accuracy_summary(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
        format: Format = "json",
    ) -> dict[str, Any] | str:
        """Aggregate accuracy (MAE, bias, std dev, RMSE, sample count). Requires API key."""
        params = self._params(
            station_id=station_id,
            city=city,
            days=days,
            date_from=date_from,
            date_to=date_to,
            format=format,
        )
        return await self._transport.get(
            "/api/v1/accuracy/summary", params=params
        )

    async def get_accuracy_by_date(
        self,
        *,
        city: str | None = None,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Accuracy per calendar day. Requires API key."""
        params = self._params(
            city=city, days=days, date_from=date_from, date_to=date_to
        )
        result = await self._transport.get(
            "/api/v1/accuracy/by-date", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_accuracy_by_date_station(
        self,
        station_id: str,
        *,
        city: str | None = None,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Accuracy per calendar day for station. Requires API key."""
        params = self._params(
            city=city, days=days, date_from=date_from, date_to=date_to
        )
        result = await self._transport.get(
            f"/api/v1/accuracy/by-date/{station_id}", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_city_accuracy(
        self,
        *,
        station_id: str | None = None,
        city: str | None = None,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
        min_samples: int = 0,
        sort_by: SortBy | None = None,
        format: Format = "json",
    ) -> dict[str, Any] | str:
        """Accuracy stats per city. Requires API key."""
        params = self._params(
            station_id=station_id,
            city=city,
            days=days,
            date_from=date_from,
            date_to=date_to,
            min_samples=min_samples,
            sort_by=sort_by,
            format=format,
        )
        return await self._transport.get(
            "/api/v1/accuracy/by-city", params=params
        )

    async def get_lead_time_accuracy(
        self,
        *,
        days: int = 90,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Accuracy by lead time bucket (0-6h, 6-12h, etc). Requires API key."""
        params = self._params(
            days=days, date_from=date_from, date_to=date_to
        )
        result = await self._transport.get(
            "/api/v1/accuracy/by-lead-time", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_station_accuracy(
        self,
        station_id: str,
        *,
        days: int = 90,
        include_raw: bool = False,
    ) -> dict[str, Any]:
        """Detailed accuracy for one station. Requires API key."""
        params = self._params(days=days, include_raw=include_raw)
        result = await self._transport.get(
            f"/api/v1/accuracy/by-station/{station_id}", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_bucket_accuracy(
        self,
        station_id: str,
        *,
        days: int = 90,
    ) -> dict[str, Any]:
        """Accuracy by 2°F temperature bucket. Requires API key."""
        params = self._params(days=days)
        result = await self._transport.get(
            f"/api/v1/accuracy/by-bucket/{station_id}", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_weather_regime_accuracy(
        self,
        *,
        station_id: str | None = None,
        days: int = 90,
    ) -> dict[str, Any]:
        """Accuracy by weather regime (clear, cloudy, precipitation, etc). Requires API key."""
        params = self._params(station_id=station_id, days=days)
        result = await self._transport.get(
            "/api/v1/accuracy/by-weather-regime", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_bias_correction(
        self,
        *,
        station_id: str | None = None,
        forecast_temp: float = 75,
        forecast_for_date: str | None = None,
        days: int = 90,
    ) -> dict[str, Any]:
        """Bias-corrected forecast with expected range. Requires API key."""
        params = self._params(
            station_id=station_id,
            forecast_temp=forecast_temp,
            forecast_for_date=forecast_for_date,
            days=days,
        )
        result = await self._transport.get(
            "/api/v1/accuracy/bias-correction", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_peak_timing(
        self,
        station_id: str,
        *,
        days: int = 90,
    ) -> dict[str, Any]:
        """Daily high timing distribution. Requires API key."""
        params = self._params(days=days)
        result = await self._transport.get(
            f"/api/v1/accuracy/peak-timing/{station_id}", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_exceedance(
        self,
        *,
        station_id: str | None = None,
        thresholds: str = "1,2,3,5",
        days: int = 90,
    ) -> dict[str, Any]:
        """Exceedance rates by °F threshold. Requires API key."""
        params = self._params(
            station_id=station_id, thresholds=thresholds, days=days
        )
        result = await self._transport.get(
            "/api/v1/accuracy/exceedance", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_sample_size(
        self,
        *,
        days: int = 90,
        min_samples: int = 0,
    ) -> dict[str, Any]:
        """Sample counts by station. Requires API key."""
        params = self._params(days=days, min_samples=min_samples)
        result = await self._transport.get(
            "/api/v1/accuracy/sample-size", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_data_freshness(self) -> dict[str, Any]:
        """Data freshness (last 24h). Requires API key."""
        result = await self._transport.get("/api/v1/accuracy/freshness")
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result

    async def get_update_frequency(
        self,
        *,
        days: int | None = None,
    ) -> dict[str, Any]:
        """Update frequency stats. Requires API key."""
        params = self._params(days=days)
        result = await self._transport.get(
            "/api/v1/accuracy/update-frequency", params=params
        )
        if isinstance(result, str):
            raise ValueError("Expected JSON response")
        return result
