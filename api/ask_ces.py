#!/usr/bin/env python3
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

from ..db import get_db
from ..schemas.dashboard import (
    CampaignInsights, DashboardChart, ChartType,
    TimeRange, MetricType, DashboardMetric
)

router = APIRouter(prefix="/ask", tags=["ask"])

class QueryRequest(BaseModel):
    """Natural language query request."""
    question: str
    time_range: Optional[TimeRange] = TimeRange.MONTH
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    """Response with insights and visualizations."""
    answer: str
    sql: Optional[str] = None
    charts: List[DashboardChart]
    metrics: List[DashboardMetric]
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

@router.post("/", response_model=QueryResponse)
async def ask_ces(
    request: QueryRequest,
    db: Session = Depends(get_db)
) -> QueryResponse:
    """Process natural language query and return insights."""
    try:
        # 1. Parse query intent
        intent = _parse_query_intent(request.question)
        
        # 2. Generate SQL
        sql = _generate_sql(intent, request.filters)
        
        # 3. Execute query
        results = _execute_query(db, sql)
        
        # 4. Generate visualizations
        charts = _create_charts(intent, results)
        
        # 5. Calculate metrics
        metrics = _calculate_metrics(intent, results)
        
        # 6. Generate narrative
        answer = _generate_narrative(intent, results, metrics)
        
        return QueryResponse(
            answer=answer,
            sql=sql,
            charts=charts,
            metrics=metrics,
            raw_data=results,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

def _parse_query_intent(question: str) -> Dict[str, Any]:
    """Parse natural language into structured intent."""
    # TODO: Implement GPT-based intent parsing
    return {
        "type": "campaign_analysis",
        "metrics": ["effectiveness", "engagement"],
        "filters": ["brand_awareness", "mothers", "mindanao"],
        "time_range": "month"
    }

def _generate_sql(intent: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> str:
    """Generate SQL from parsed intent."""
    # TODO: Implement GPT-based SQL generation
    return """
    SELECT
        c.campaign_id,
        c.name AS campaign_name,
        COUNT(at.asset_id) AS num_assets,
        AVG(f.effectiveness_score) AS avg_effectiveness
    FROM campaigns c
    JOIN campaign_tags ct ON ct.campaign_id = c.campaign_id
    JOIN tags t ON t.tag_id = ct.tag_id
    LEFT JOIN asset_tags at ON at.tag_id = t.tag_id
    LEFT JOIN features f ON f.asset_id = at.asset_id
    WHERE t.name IN ('brand_awareness', 'mothers', 'mindanao')
    GROUP BY c.campaign_id, c.name
    ORDER BY avg_effectiveness DESC
    LIMIT 5
    """

def _execute_query(db: Session, sql: str) -> Dict[str, Any]:
    """Execute SQL query and return results."""
    # TODO: Implement safe query execution
    return {
        "campaigns": [
            {
                "campaign_id": "123",
                "campaign_name": "Sample Campaign",
                "num_assets": 42,
                "avg_effectiveness": 0.85
            }
        ]
    }

def _create_charts(intent: Dict[str, Any], results: Dict[str, Any]) -> List[DashboardChart]:
    """Create visualization charts based on results."""
    charts = []
    
    # Add effectiveness chart
    charts.append(
        DashboardChart(
            id="effectiveness",
            title="Campaign Effectiveness",
            description="Effectiveness scores by campaign",
            type=ChartType.BAR,
            data_source="campaigns",
            x_axis="campaign_name",
            y_axis="avg_effectiveness"
        )
    )
    
    # Add asset distribution chart
    charts.append(
        DashboardChart(
            id="assets",
            title="Asset Distribution",
            description="Number of assets by campaign",
            type=ChartType.PIE,
            data_source="campaigns",
            x_axis="campaign_name",
            y_axis="num_assets"
        )
    )
    
    return charts

def _calculate_metrics(intent: Dict[str, Any], results: Dict[str, Any]) -> List[DashboardMetric]:
    """Calculate key metrics from results."""
    metrics = []
    
    # Add total campaigns metric
    metrics.append(
        DashboardMetric(
            id="total_campaigns",
            name="Total Campaigns",
            description="Number of matching campaigns",
            type=MetricType.COUNT,
            value=len(results["campaigns"]),
            last_updated=datetime.utcnow()
        )
    )
    
    # Add average effectiveness metric
    avg_effectiveness = sum(
        c["avg_effectiveness"] for c in results["campaigns"]
    ) / len(results["campaigns"])
    
    metrics.append(
        DashboardMetric(
            id="avg_effectiveness",
            name="Average Effectiveness",
            description="Mean effectiveness score",
            type=MetricType.AVERAGE,
            value=avg_effectiveness,
            last_updated=datetime.utcnow()
        )
    )
    
    return metrics

def _generate_narrative(
    intent: Dict[str, Any],
    results: Dict[str, Any],
    metrics: List[DashboardMetric]
) -> str:
    """Generate natural language narrative from results."""
    # TODO: Implement GPT-based narrative generation
    return f"""
    Found {metrics[0].value} campaigns matching your criteria.
    The average effectiveness score is {metrics[1].value:.2f}.
    Top performing campaign: {results['campaigns'][0]['campaign_name']}
    with {results['campaigns'][0]['num_assets']} assets.
    """ 