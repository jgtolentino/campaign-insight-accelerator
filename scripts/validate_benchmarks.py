#!/usr/bin/env python3
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# ——— CONFIG ———
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/cesdb")
BENCHMARK_FILE = "creative_benchmarks.json"

# ——— MODELS ———
Base = declarative_base()

class BenchmarkSource(Enum):
    SALES_LIFT = "sales_lift"
    BRAND_TRACKING = "brand_tracking"
    ENGAGEMENT = "engagement"
    AWARD = "award"
    PLATFORM = "platform"

class BenchmarkType(Enum):
    ROI = "roi"
    BRAND_RECALL = "brand_recall"
    CONSIDERATION = "consideration"
    CTR = "ctr"
    COMPLETION_RATE = "completion_rate"
    VIEW_THROUGH = "view_through"
    CONVERSION_LIFT = "conversion_lift"

@dataclass
class Benchmark:
    source: BenchmarkSource
    type: BenchmarkType
    value: float
    confidence: float  # 0-1 scale
    sample_size: Optional[int]
    date: datetime
    metadata: Dict

class CampaignBenchmark(Base):
    __tablename__ = "campaign_benchmarks"
    
    id = sa.Column(sa.Integer, primary_key=True)
    campaign_id = sa.Column(sa.String, nullable=False)
    benchmark_type = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.Float, nullable=False)
    confidence = sa.Column(sa.Float, nullable=False)
    source = sa.Column(sa.String, nullable=False)
    sample_size = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime, nullable=False)
    metadata = sa.Column(sa.JSON)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

# ——— BENCHMARK VALIDATION ———
class BenchmarkValidator:
    def __init__(self, db_url: str):
        self.engine = sa.create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        
        # Industry standard thresholds
        self.thresholds = {
            BenchmarkType.ROI: {
                "excellent": 3.0,  # 300% ROI
                "good": 2.0,      # 200% ROI
                "average": 1.0    # 100% ROI
            },
            BenchmarkType.BRAND_RECALL: {
                "excellent": 0.75,  # 75%
                "good": 0.60,      # 60%
                "average": 0.45    # 45%
            },
            BenchmarkType.CTR: {
                "excellent": 0.05,  # 5%
                "good": 0.03,      # 3%
                "average": 0.02    # 2%
            },
            BenchmarkType.COMPLETION_RATE: {
                "excellent": 0.85,  # 85%
                "good": 0.70,      # 70%
                "average": 0.50    # 50%
            }
        }

    def validate_benchmark(self, benchmark: Benchmark) -> Dict:
        """Validate a benchmark against industry standards."""
        if benchmark.type not in self.thresholds:
            return {
                "valid": True,
                "message": f"No industry thresholds for {benchmark.type.value}",
                "rating": "unknown"
            }
        
        thresholds = self.thresholds[benchmark.type]
        
        # Check if value is within reasonable bounds
        if benchmark.value < 0:
            return {
                "valid": False,
                "message": f"Negative {benchmark.type.value} value",
                "rating": "invalid"
            }
        
        # Determine rating based on thresholds
        if benchmark.value >= thresholds["excellent"]:
            rating = "excellent"
        elif benchmark.value >= thresholds["good"]:
            rating = "good"
        elif benchmark.value >= thresholds["average"]:
            rating = "average"
        else:
            rating = "below_average"
        
        return {
            "valid": True,
            "message": f"Valid {benchmark.type.value} benchmark",
            "rating": rating,
            "thresholds": thresholds
        }

    def save_benchmark(self, campaign_id: str, benchmark: Benchmark):
        """Save a validated benchmark to the database."""
        validation = self.validate_benchmark(benchmark)
        
        if not validation["valid"]:
            print(f"⚠️  Invalid benchmark: {validation['message']}")
            return
        
        db_benchmark = CampaignBenchmark(
            campaign_id=campaign_id,
            benchmark_type=benchmark.type.value,
            value=benchmark.value,
            confidence=benchmark.confidence,
            source=benchmark.source.value,
            sample_size=benchmark.sample_size,
            date=benchmark.date,
            metadata={
                "validation": validation,
                **benchmark.metadata
            }
        )
        
        self.session.add(db_benchmark)
        self.session.commit()
        print(f"✅ Saved {benchmark.type.value} benchmark for campaign {campaign_id}")

    def get_campaign_benchmarks(self, campaign_id: str) -> List[Dict]:
        """Retrieve all benchmarks for a campaign."""
        benchmarks = self.session.query(CampaignBenchmark)\
            .filter_by(campaign_id=campaign_id)\
            .order_by(CampaignBenchmark.date.desc())\
            .all()
        
        return [{
            "type": b.benchmark_type,
            "value": b.value,
            "confidence": b.confidence,
            "source": b.source,
            "date": b.date.isoformat(),
            "rating": b.metadata.get("validation", {}).get("rating", "unknown")
        } for b in benchmarks]

    def generate_report(self, campaign_id: str) -> Dict:
        """Generate a comprehensive benchmark report."""
        benchmarks = self.get_campaign_benchmarks(campaign_id)
        
        if not benchmarks:
            return {
                "campaign_id": campaign_id,
                "status": "no_benchmarks",
                "message": "No benchmarks found for this campaign"
            }
        
        # Calculate aggregate metrics
        by_type = {}
        for b in benchmarks:
            if b["type"] not in by_type:
                by_type[b["type"]] = []
            by_type[b["type"]].append(b)
        
        report = {
            "campaign_id": campaign_id,
            "status": "complete",
            "benchmark_types": len(by_type),
            "total_benchmarks": len(benchmarks),
            "by_type": {}
        }
        
        # Analyze each benchmark type
        for btype, values in by_type.items():
            latest = max(values, key=lambda x: x["date"])
            avg_value = sum(b["value"] for b in values) / len(values)
            avg_confidence = sum(b["confidence"] for b in values) / len(values)
            
            report["by_type"][btype] = {
                "latest": latest,
                "average_value": avg_value,
                "average_confidence": avg_confidence,
                "count": len(values)
            }
        
        return report

def main():
    validator = BenchmarkValidator(DATABASE_URL)
    
    # Example usage
    benchmark = Benchmark(
        source=BenchmarkSource.SALES_LIFT,
        type=BenchmarkType.ROI,
        value=2.5,  # 250% ROI
        confidence=0.85,
        sample_size=1000,
        date=datetime.utcnow(),
        metadata={"test_type": "geo_test", "duration_days": 30}
    )
    
    validator.save_benchmark("campaign_123", benchmark)
    report = validator.generate_report("campaign_123")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main() 