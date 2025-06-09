#!/usr/bin/env python3
"""
Full Dataset Generator for Campaign Insight Accelerator
Generates comprehensive mock data for CES monitoring and campaign analytics
"""

import json
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import os

class FullDatasetGenerator:
    def __init__(self):
        self.output_dir = Path("data")
        self.output_dir.mkdir(exist_ok=True)
        
        # Campaign categories and types
        self.campaign_types = ["Brand Awareness", "Product Launch", "Seasonal", "Digital", "Social Media", "TV Commercial"]
        self.industries = ["FMCG", "Automotive", "Tech", "Healthcare", "Fashion", "Finance", "Food & Beverage"]
        self.regions = ["Global", "APAC", "North America", "Europe", "LATAM", "MEA"]
        self.brands = ["CocaCola", "Nike", "Apple", "Samsung", "Toyota", "Unilever", "P&G", "McDonald's", "Adidas", "BMW"]
        
        # Performance metrics ranges
        self.metric_ranges = {
            "roi": (0.8, 8.5),
            "brand_recall": (15, 85),
            "engagement_rate": (0.5, 12.0),
            "reach": (100000, 50000000),
            "ctr": (0.1, 8.5),
            "conversion_rate": (0.5, 15.0),
            "cost_per_acquisition": (5, 500),
            "sentiment_score": (0.1, 1.0)
        }

    def generate_campaigns(self, num_campaigns=500):
        """Generate campaign data"""
        campaigns = []
        
        for i in range(num_campaigns):
            start_date = datetime.now() - timedelta(days=random.randint(30, 1095))
            end_date = start_date + timedelta(days=random.randint(7, 180))
            
            campaign = {
                "campaign_id": str(uuid.uuid4()),
                "name": f"{random.choice(self.brands)} {random.choice(self.campaign_types)} {start_date.year}",
                "brand": random.choice(self.brands),
                "industry": random.choice(self.industries),
                "type": random.choice(self.campaign_types),
                "region": random.choice(self.regions),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "budget": random.randint(50000, 5000000),
                "status": random.choice(["Active", "Completed", "Paused", "Planning"]),
                "tenant_id": random.choice(["tbwa", "ces", "scout"]),
                "created_at": (start_date - timedelta(days=random.randint(1, 30))).isoformat()
            }
            campaigns.append(campaign)
        
        return campaigns

    def generate_performance_metrics(self, campaigns):
        """Generate performance metrics for campaigns"""
        metrics = []
        
        for campaign in campaigns:
            # Generate daily metrics for campaign duration
            start = datetime.fromisoformat(campaign["start_date"])
            end = datetime.fromisoformat(campaign["end_date"])
            current = start
            
            while current <= end:
                # Add some noise based on campaign type and brand
                brand_multiplier = 1.2 if campaign["brand"] in ["Apple", "Nike", "CocaCola"] else 1.0
                type_multiplier = 1.3 if campaign["type"] in ["Digital", "Social Media"] else 1.0
                
                metric = {
                    "metric_id": str(uuid.uuid4()),
                    "campaign_id": campaign["campaign_id"],
                    "date": current.isoformat(),
                    "roi": round(random.uniform(*self.metric_ranges["roi"]) * brand_multiplier, 2),
                    "brand_recall": round(random.uniform(*self.metric_ranges["brand_recall"]) * brand_multiplier, 1),
                    "engagement_rate": round(random.uniform(*self.metric_ranges["engagement_rate"]) * type_multiplier, 2),
                    "reach": int(random.uniform(*self.metric_ranges["reach"]) * brand_multiplier),
                    "impressions": int(random.uniform(50000, 10000000) * brand_multiplier),
                    "clicks": int(random.uniform(500, 500000) * type_multiplier),
                    "ctr": round(random.uniform(*self.metric_ranges["ctr"]) * type_multiplier, 2),
                    "conversion_rate": round(random.uniform(*self.metric_ranges["conversion_rate"]), 2),
                    "cost_per_acquisition": round(random.uniform(*self.metric_ranges["cost_per_acquisition"]), 2),
                    "sentiment_score": round(random.uniform(*self.metric_ranges["sentiment_score"]), 3),
                    "video_completion_rate": round(random.uniform(25, 95), 1),
                    "share_rate": round(random.uniform(0.1, 5.0), 2),
                    "save_rate": round(random.uniform(0.5, 8.0), 2),
                    "tenant_id": campaign["tenant_id"]
                }
                metrics.append(metric)
                current += timedelta(days=1)
        
        return metrics

    def generate_creative_assets(self, campaigns):
        """Generate creative assets data"""
        assets = []
        asset_types = ["video", "image", "banner", "social_post", "infographic", "gif", "story"]
        
        for campaign in campaigns:
            # Generate 3-15 assets per campaign
            num_assets = random.randint(3, 15)
            
            for i in range(num_assets):
                asset = {
                    "asset_id": str(uuid.uuid4()),
                    "campaign_id": campaign["campaign_id"],
                    "name": f"{campaign['name']}_asset_{i+1}",
                    "type": random.choice(asset_types),
                    "format": random.choice(["jpg", "png", "mp4", "gif", "svg"]),
                    "size_mb": round(random.uniform(0.1, 50.0), 2),
                    "dimensions": f"{random.choice([1080, 1920, 728, 300])}x{random.choice([1080, 1920, 90, 250])}",
                    "duration_seconds": random.randint(5, 60) if asset_types[assets.__len__() % len(asset_types)] == "video" else None,
                    "emotional_trigger": random.choice(["Joy", "Trust", "Excitement", "Nostalgia", "Surprise", "Fear"]),
                    "brand_integration": random.choice(["Subtle", "Moderate", "Prominent", "Minimal"]),
                    "visual_distinctness": round(random.uniform(0.1, 1.0), 2),
                    "text_readability": round(random.uniform(0.3, 1.0), 2),
                    "color_harmony": round(random.uniform(0.4, 1.0), 2),
                    "performance_score": round(random.uniform(0.2, 0.95), 3),
                    "a_b_test_variant": random.choice(["A", "B", "C", "Control"]) if random.random() > 0.7 else None,
                    "tenant_id": campaign["tenant_id"],
                    "created_at": datetime.now().isoformat()
                }
                assets.append(asset)
        
        return assets

    def generate_sensors_data(self):
        """Generate sensor monitoring data for pipeline health"""
        sensors = []
        sensor_types = ["data_freshness", "model_accuracy", "api_latency", "data_quality", "throughput"]
        
        # Generate sensor data for last 30 days
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            for sensor_type in sensor_types:
                # Generate multiple readings per day
                for hour in range(0, 24, 4):  # Every 4 hours
                    sensor_time = current_date.replace(hour=hour, minute=0, second=0)
                    
                    # Sensor-specific value generation
                    if sensor_type == "data_freshness":
                        value = random.uniform(0.85, 1.0)
                        status = "OK" if value > 0.9 else "WARN" if value > 0.8 else "FAIL"
                    elif sensor_type == "model_accuracy":
                        value = random.uniform(0.75, 0.95)
                        status = "OK" if value > 0.85 else "WARN" if value > 0.8 else "FAIL"
                    elif sensor_type == "api_latency":
                        value = random.uniform(50, 500)  # milliseconds
                        status = "OK" if value < 200 else "WARN" if value < 350 else "FAIL"
                    elif sensor_type == "data_quality":
                        value = random.uniform(0.8, 1.0)
                        status = "OK" if value > 0.95 else "WARN" if value > 0.9 else "FAIL"
                    else:  # throughput
                        value = random.uniform(800, 1200)  # requests per minute
                        status = "OK" if value > 1000 else "WARN" if value > 900 else "FAIL"
                    
                    sensor = {
                        "sensor_id": str(uuid.uuid4()),
                        "sensor_type": sensor_type,
                        "timestamp": sensor_time.isoformat(),
                        "value": round(value, 3),
                        "status": status,
                        "tenant_id": random.choice(["tbwa", "ces", "scout"]),
                        "metadata": {
                            "pipeline": f"ces_{sensor_type}_pipeline",
                            "environment": "production",
                            "region": random.choice(["us-east-1", "eu-west-1", "ap-southeast-1"])
                        }
                    }
                    sensors.append(sensor)
        
        return sensors

    def generate_model_performance(self):
        """Generate model performance tracking data"""
        models = []
        model_types = ["engagement_predictor", "roi_optimizer", "sentiment_analyzer", "creative_scorer", "audience_segmenter"]
        
        for model_type in model_types:
            # Generate model performance over time
            for day in range(30):
                date = (datetime.now() - timedelta(days=day))
                
                # Simulate model drift and retraining
                base_accuracy = 0.85
                drift = random.uniform(-0.05, 0.02)  # Gradual drift down, occasional improvement
                
                model = {
                    "model_id": str(uuid.uuid4()),
                    "model_type": model_type,
                    "version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    "date": date.isoformat(),
                    "accuracy": round(base_accuracy + drift, 4),
                    "precision": round(random.uniform(0.8, 0.95), 4),
                    "recall": round(random.uniform(0.75, 0.92), 4),
                    "f1_score": round(random.uniform(0.78, 0.93), 4),
                    "latency_ms": random.randint(50, 300),
                    "throughput_rps": random.randint(100, 1000),
                    "training_time_hours": round(random.uniform(0.5, 8.0), 2),
                    "training_data_size": random.randint(10000, 1000000),
                    "feature_count": random.randint(15, 150),
                    "last_retrained": (date - timedelta(days=random.randint(1, 14))).isoformat(),
                    "status": random.choice(["active", "deprecated", "testing", "training"]),
                    "tenant_id": random.choice(["tbwa", "ces", "scout"])
                }
                models.append(model)
        
        return models

    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Generated {len(data)} records in {filepath}")

    def save_to_csv(self, data, filename):
        """Save data to CSV file"""
        if not data:
            return
            
        filepath = self.output_dir / f"{filename}.csv"
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Generated {len(data)} records in {filepath}")

    def generate_full_dataset(self):
        """Generate complete dataset for CES monitoring"""
        print("🚀 Starting full dataset generation...")
        
        # Generate core data
        print("\n📊 Generating campaigns...")
        campaigns = self.generate_campaigns(500)
        self.save_to_json(campaigns, "campaigns")
        self.save_to_csv(campaigns, "campaigns")
        
        print("\n📈 Generating performance metrics...")
        metrics = self.generate_performance_metrics(campaigns)
        self.save_to_json(metrics, "performance_metrics")
        self.save_to_csv(metrics, "performance_metrics")
        
        print("\n🎨 Generating creative assets...")
        assets = self.generate_creative_assets(campaigns)
        self.save_to_json(assets, "creative_assets")
        self.save_to_csv(assets, "creative_assets")
        
        print("\n🔍 Generating sensor monitoring data...")
        sensors = self.generate_sensors_data()
        self.save_to_json(sensors, "sensor_data")
        self.save_to_csv(sensors, "sensor_data")
        
        print("\n🤖 Generating model performance data...")
        models = self.generate_model_performance()
        self.save_to_json(models, "model_performance")
        self.save_to_csv(models, "model_performance")
        
        # Generate summary statistics
        summary = {
            "generation_timestamp": datetime.now().isoformat(),
            "total_campaigns": len(campaigns),
            "total_metrics": len(metrics),
            "total_assets": len(assets),
            "total_sensors": len(sensors),
            "total_models": len(models),
            "date_range": {
                "start": min(c["start_date"] for c in campaigns),
                "end": max(c["end_date"] for c in campaigns)
            },
            "tenants": ["tbwa", "ces", "scout"],
            "brands": self.brands,
            "industries": self.industries
        }
        
        self.save_to_json(summary, "dataset_summary")
        
        print(f"\n🎉 Full dataset generation complete!")
        print(f"📁 Files saved to: {self.output_dir.absolute()}")
        print(f"📊 Total records: {sum([len(campaigns), len(metrics), len(assets), len(sensors), len(models)])}")

if __name__ == "__main__":
    generator = FullDatasetGenerator()
    generator.generate_full_dataset()