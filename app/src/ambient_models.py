"""Pydantic models for the E2-5 ambient cycle admin API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AmbientConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    global_enabled: bool
    cycle_window_start: str
    cycle_window_end: str
    cycle_window_tz: str
    global_frequency_min: int
    per_workspace_frequency_min: int
    budget_pct_of_router_daily: float
    max_proposals_per_cycle: int
    dark_launch_days: int
    utility_threshold_pct: int
    cost_overrun_pct: int


class AmbientConfigUpdate(BaseModel):
    global_enabled: bool | None = None
    cycle_window_start: str | None = Field(default=None, max_length=10)
    cycle_window_end: str | None = Field(default=None, max_length=10)
    cycle_window_tz: str | None = Field(default=None, max_length=64)
    global_frequency_min: int | None = Field(default=None, ge=15)
    per_workspace_frequency_min: int | None = Field(default=None, ge=30)
    budget_pct_of_router_daily: float | None = Field(default=None, ge=1.0)
    max_proposals_per_cycle: int | None = Field(default=None, ge=3)
    dark_launch_days: int | None = Field(default=None, ge=0)
    utility_threshold_pct: int | None = Field(default=None, ge=0, le=100)
    cost_overrun_pct: int | None = Field(default=None, ge=100)


class AmbientWorkspaceConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str
    enabled: bool
    detector_allowlist: list[str]
    excluded_detector_slugs: list[str]


class AmbientWorkspaceConfigUpdate(BaseModel):
    enabled: bool | None = None
    detector_allowlist: list[str] | None = None
    excluded_detector_slugs: list[str] | None = None


class AmbientKillSwitchRequest(BaseModel):
    enabled: bool


class AmbientTriggerRequest(BaseModel):
    workspace_id: str | None = None
    trigger: str = "manual"


class AmbientTriggerResponse(BaseModel):
    cycle_id: str
    status: str
    proposals_created: int


class AmbientCycleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    workspace_id: str | None
    status: str
    trigger: str
    started_at: str
    ended_at: str | None
    detectors_run: int
    detectors_failed: int
    proposals_created: int
    proposals_visible: int
    proposals_dark: int
    cost_usd: float
    budget_usd: float


class AmbientMetricsRead(BaseModel):
    tenant_id: str
    workspace_id: str | None
    period_days: int
    proposals_created: int
    proposals_visible: int
    proposals_accepted: int
    proposals_ignored: int
    utility_pct: float
    noise_pct: float
    cost_usd: float
    budget_usd: float
