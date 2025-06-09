#!/usr/bin/env python3
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"

class TimeRange(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL = "all"

class MetricType(Enum):
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"

class DashboardMetric(BaseModel):
    """Base class for dashboard metrics."""
    id: str
    name: str
    description: str
    type: MetricType
    value: float
    trend: Optional[float] = None
    change_period: Optional[TimeRange] = None
    last_updated: datetime

class AssetDistribution(BaseModel):
    """Asset type distribution metrics."""
    total_assets: int
    by_type: Dict[str, int]
    by_owner: Dict[str, int]
    by_depth: Dict[int, int]
    shared_count: int
    unviewed_count: int
    last_updated: datetime

class TimeSeriesMetric(BaseModel):
    """Time-based metric for trend analysis."""
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    period: TimeRange
    aggregation: MetricType

class DashboardChart(BaseModel):
    """Chart configuration for dashboard."""
    id: str
    title: str
    description: str
    type: ChartType
    data_source: str
    x_axis: str
    y_axis: str
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    time_range: TimeRange = TimeRange.MONTH

class DashboardPanel(BaseModel):
    """Dashboard panel configuration."""
    id: str
    title: str
    description: str
    layout: Dict[str, int]  # x, y, w, h
    charts: List[DashboardChart]
    metrics: List[DashboardMetric]

class CampaignInsights(BaseModel):
    """Campaign asset insights schema."""
    # Overview metrics
    total_assets: int
    total_size_gb: float
    unique_owners: int
    active_campaigns: int
    
    # Asset distribution
    asset_distribution: AssetDistribution
    
    # Time series
    asset_growth: TimeSeriesMetric
    sharing_trend: TimeSeriesMetric
    engagement_trend: TimeSeriesMetric
    
    # Performance metrics
    avg_folder_depth: float
    shared_percentage: float
    engagement_rate: float
    
    # Charts
    charts: List[DashboardChart] = Field(default_factory=list)
    
    # Panels
    panels: List[DashboardPanel] = Field(default_factory=list)

def create_default_dashboard() -> CampaignInsights:
    """Create default dashboard configuration."""
    return CampaignInsights(
        total_assets=0,
        total_size_gb=0.0,
        unique_owners=0,
        active_campaigns=0,
        asset_distribution=AssetDistribution(
            total_assets=0,
            by_type={},
            by_owner={},
            by_depth={},
            shared_count=0,
            unviewed_count=0,
            last_updated=datetime.utcnow()
        ),
        asset_growth=TimeSeriesMetric(
            metric_name="asset_growth",
            values=[],
            timestamps=[],
            period=TimeRange.MONTH,
            aggregation=MetricType.COUNT
        ),
        sharing_trend=TimeSeriesMetric(
            metric_name="sharing_trend",
            values=[],
            timestamps=[],
            period=TimeRange.MONTH,
            aggregation=MetricType.PERCENTAGE
        ),
        engagement_trend=TimeSeriesMetric(
            metric_name="engagement_trend",
            values=[],
            timestamps=[],
            period=TimeRange.MONTH,
            aggregation=MetricType.AVERAGE
        ),
        avg_folder_depth=0.0,
        shared_percentage=0.0,
        engagement_rate=0.0,
        charts=[
            DashboardChart(
                id="asset_types",
                title="Asset Type Distribution",
                description="Distribution of assets by type",
                type=ChartType.PIE,
                data_source="asset_distribution.by_type",
                x_axis="type",
                y_axis="count"
            ),
            DashboardChart(
                id="folder_depth",
                title="Folder Depth Analysis",
                description="Distribution of assets by folder depth",
                type=ChartType.BAR,
                data_source="asset_distribution.by_depth",
                x_axis="depth",
                y_axis="count"
            ),
            DashboardChart(
                id="sharing_trend",
                title="Sharing Trend",
                description="Trend of shared assets over time",
                type=ChartType.LINE,
                data_source="sharing_trend",
                x_axis="timestamp",
                y_axis="value"
            ),
            DashboardChart(
                id="owner_distribution",
                title="Owner Distribution",
                description="Assets by owner",
                type=ChartType.TREEMAP,
                data_source="asset_distribution.by_owner",
                x_axis="owner",
                y_axis="count",
                size_by="count"
            )
        ],
        panels=[
            DashboardPanel(
                id="overview",
                title="Campaign Overview",
                description="Key metrics and trends",
                layout={"x": 0, "y": 0, "w": 12, "h": 4},
                charts=[
                    DashboardChart(
                        id="asset_growth",
                        title="Asset Growth",
                        description="Growth of assets over time",
                        type=ChartType.LINE,
                        data_source="asset_growth",
                        x_axis="timestamp",
                        y_axis="value"
                    )
                ],
                metrics=[
                    DashboardMetric(
                        id="total_assets",
                        name="Total Assets",
                        description="Total number of assets",
                        type=MetricType.COUNT,
                        value=0,
                        last_updated=datetime.utcnow()
                    ),
                    DashboardMetric(
                        id="shared_percentage",
                        name="Shared Assets",
                        description="Percentage of shared assets",
                        type=MetricType.PERCENTAGE,
                        value=0,
                        last_updated=datetime.utcnow()
                    )
                ]
            )
        ]
    ) 