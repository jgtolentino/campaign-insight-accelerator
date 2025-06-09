#!/usr/bin/env python3
import os
import json
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

# ——— CONFIG ———
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/cesdb")
Base = declarative_base()

# ——— MODELS ———
class CreativeFeature(Base):
    __tablename__ = "creative_features"
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text)
    category = sa.Column(sa.String)  # visual, audio, narrative, etc.
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CampaignAsset(Base):
    __tablename__ = "campaign_assets"
    
    asset_id = sa.Column(sa.String, primary_key=True)
    file_id = sa.Column(sa.String, nullable=False)
    file_name = sa.Column(sa.String, nullable=False)
    file_type = sa.Column(sa.String, nullable=False)
    mime_type = sa.Column(sa.String, nullable=False)
    campaign_folder = sa.Column(sa.String, nullable=False)
    tenant_id = sa.Column(sa.String, nullable=False)
    size_bytes = sa.Column(sa.BigInteger)
    modified_time = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssetFeature(Base):
    __tablename__ = "asset_features"
    
    id = sa.Column(sa.Integer, primary_key=True)
    asset_id = sa.Column(sa.String, sa.ForeignKey("campaign_assets.asset_id"))
    feature_id = sa.Column(sa.Integer, sa.ForeignKey("creative_features.id"))
    value = sa.Column(sa.Float)  # Feature value or presence
    confidence = sa.Column(sa.Float)  # Detection confidence
    source = sa.Column(sa.String)  # How this was detected
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

class Benchmark(Base):
    __tablename__ = "benchmarks"
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)  # roi, brand_recall, etc.
    value = sa.Column(sa.Float, nullable=False)
    confidence = sa.Column(sa.Float)
    source = sa.Column(sa.String)  # sales_lift, brand_tracking, etc.
    sample_size = sa.Column(sa.Integer)
    date = sa.Column(sa.DateTime, nullable=False)
    metadata = sa.Column(sa.JSON)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

class FeatureImpact(Base):
    __tablename__ = "feature_impacts"
    
    id = sa.Column(sa.Integer, primary_key=True)
    feature_id = sa.Column(sa.Integer, sa.ForeignKey("creative_features.id"))
    benchmark_id = sa.Column(sa.Integer, sa.ForeignKey("benchmarks.id"))
    impact_score = sa.Column(sa.Float)  # SHAP value or similar
    confidence = sa.Column(sa.Float)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

class DataMartBuilder:
    def __init__(self, db_url: str):
        self.engine = sa.create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def seed_creative_features(self):
        """Seed the core creative features we track."""
        features = [
            {
                "name": "emotional_trigger",
                "description": "Content designed to evoke emotional response",
                "category": "narrative"
            },
            {
                "name": "brand_integration",
                "description": "How prominently the brand is featured",
                "category": "visual"
            },
            {
                "name": "visual_distinctness",
                "description": "Unique visual elements that stand out",
                "category": "visual"
            },
            {
                "name": "story_arc",
                "description": "Presence of clear narrative structure",
                "category": "narrative"
            },
            {
                "name": "audio_impact",
                "description": "Effectiveness of sound design",
                "category": "audio"
            }
        ]
        
        for f in features:
            feature = CreativeFeature(**f)
            self.session.merge(feature)
        self.session.commit()
        print(f"✅ Seeded {len(features)} creative features")

    def load_assets(self, csv_path: str):
        """Load campaign assets from CSV."""
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            asset = CampaignAsset(
                asset_id=row['asset_id'],
                file_id=row['file_id'],
                file_name=row['file_name'],
                file_type=row['file_type'],
                mime_type=row['mime_type'],
                campaign_folder=row['campaign_folder'],
                tenant_id=row['tenant_id'],
                size_bytes=row.get('size_bytes'),
                modified_time=pd.to_datetime(row.get('modified_time')) if row.get('modified_time') else None
            )
            self.session.merge(asset)
        self.session.commit()
        print(f"✅ Loaded {len(df)} campaign assets")

    def seed_benchmarks(self):
        """Seed industry standard benchmarks."""
        benchmarks = [
            {
                "name": "High ROI Campaign",
                "type": "roi",
                "value": 3.0,  # 300% ROI
                "confidence": 0.95,
                "source": "sales_lift",
                "sample_size": 1000,
                "date": datetime.utcnow(),
                "metadata": {"industry": "FMCG", "duration_days": 30}
            },
            {
                "name": "Strong Brand Recall",
                "type": "brand_recall",
                "value": 0.75,  # 75%
                "confidence": 0.90,
                "source": "brand_tracking",
                "sample_size": 500,
                "date": datetime.utcnow(),
                "metadata": {"industry": "Retail", "method": "aided_recall"}
            }
        ]
        
        for b in benchmarks:
            benchmark = Benchmark(**b)
            self.session.merge(benchmark)
        self.session.commit()
        print(f"✅ Seeded {len(benchmarks)} benchmarks")

    def compute_feature_impacts(self):
        """Compute feature importance scores based on benchmarks."""
        # This would typically involve ML model training
        # For now, we'll use some example impacts
        impacts = [
            {
                "feature_id": 1,  # emotional_trigger
                "benchmark_id": 1,  # High ROI Campaign
                "impact_score": 0.85,
                "confidence": 0.90
            },
            {
                "feature_id": 2,  # brand_integration
                "benchmark_id": 2,  # Strong Brand Recall
                "impact_score": 0.92,
                "confidence": 0.95
            }
        ]
        
        for i in impacts:
            impact = FeatureImpact(**i)
            self.session.merge(impact)
        self.session.commit()
        print(f"✅ Computed {len(impacts)} feature impacts")

    def generate_report(self) -> Dict:
        """Generate a data mart health report."""
        stats = {
            "assets": self.session.query(CampaignAsset).count(),
            "features": self.session.query(CreativeFeature).count(),
            "benchmarks": self.session.query(Benchmark).count(),
            "impacts": self.session.query(FeatureImpact).count()
        }
        
        # Get feature coverage
        feature_coverage = self.session.query(
            CreativeFeature.name,
            sa.func.count(AssetFeature.id).label('count')
        ).outerjoin(AssetFeature).group_by(CreativeFeature.name).all()
        
        return {
            "status": "complete",
            "stats": stats,
            "feature_coverage": {f.name: f.count for f in feature_coverage}
        }

def main():
    builder = DataMartBuilder(DATABASE_URL)
    
    # Build the data mart
    builder.seed_creative_features()
    builder.load_assets("dataset_campaign_assets.csv")
    builder.seed_benchmarks()
    builder.compute_feature_impacts()
    
    # Generate report
    report = builder.generate_report()
    print("\n📊 Data Mart Health Report:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main() 