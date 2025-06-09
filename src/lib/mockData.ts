// Mock data loader for Campaign Insight Accelerator
// This provides the generated dataset to the frontend components

export interface Campaign {
  campaign_id: string;
  name: string;
  brand: string;
  industry: string;
  type: string;
  region: string;
  start_date: string;
  end_date: string;
  budget: number;
  status: string;
  tenant_id: string;
  created_at: string;
}

export interface PerformanceMetric {
  metric_id: string;
  campaign_id: string;
  date: string;
  roi: number;
  brand_recall: number;
  engagement_rate: number;
  reach: number;
  impressions: number;
  clicks: number;
  ctr: number;
  conversion_rate: number;
  cost_per_acquisition: number;
  sentiment_score: number;
  video_completion_rate: number;
  share_rate: number;
  save_rate: number;
  tenant_id: string;
}

export interface CreativeAsset {
  asset_id: string;
  campaign_id: string;
  name: string;
  type: string;
  format: string;
  size_mb: number;
  dimensions: string;
  duration_seconds?: number;
  emotional_trigger: string;
  brand_integration: string;
  visual_distinctness: number;
  text_readability: number;
  color_harmony: number;
  performance_score: number;
  a_b_test_variant?: string;
  tenant_id: string;
  created_at: string;
}

export interface SensorData {
  sensor_id: string;
  sensor_type: string;
  timestamp: string;
  value: number;
  status: 'OK' | 'WARN' | 'FAIL';
  tenant_id: string;
  metadata: {
    pipeline: string;
    environment: string;
    region: string;
  };
}

export interface ModelPerformance {
  model_id: string;
  model_type: string;
  version: string;
  date: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  latency_ms: number;
  throughput_rps: number;
  training_time_hours: number;
  training_data_size: number;
  feature_count: number;
  last_retrained: string;
  status: string;
  tenant_id: string;
}

// Mock data samples for development
export const mockCampaigns: Campaign[] = [
  {
    campaign_id: "123e4567-e89b-12d3-a456-426614174000",
    name: "Nike Digital 2024",
    brand: "Nike",
    industry: "Fashion",
    type: "Digital",
    region: "Global",
    start_date: "2024-01-15T00:00:00",
    end_date: "2024-03-15T00:00:00",
    budget: 2500000,
    status: "Completed",
    tenant_id: "tbwa",
    created_at: "2024-01-01T00:00:00"
  }
];

export const mockSensorData: SensorData[] = [
  {
    sensor_id: "sensor-001",
    sensor_type: "data_freshness",
    timestamp: new Date().toISOString(),
    value: 0.95,
    status: "OK",
    tenant_id: "ces",
    metadata: {
      pipeline: "ces_data_freshness_pipeline",
      environment: "production",
      region: "us-east-1"
    }
  },
  {
    sensor_id: "sensor-002",
    sensor_type: "model_accuracy",
    timestamp: new Date().toISOString(),
    value: 0.87,
    status: "OK",
    tenant_id: "ces",
    metadata: {
      pipeline: "ces_model_accuracy_pipeline",
      environment: "production",
      region: "us-east-1"
    }
  },
  {
    sensor_id: "sensor-003",
    sensor_type: "api_latency",
    timestamp: new Date().toISOString(),
    value: 145,
    status: "OK",
    tenant_id: "ces",
    metadata: {
      pipeline: "ces_api_latency_pipeline",
      environment: "production",
      region: "us-east-1"
    }
  }
];

// Data loading utilities
import { loadRealDataset, getDashboardSummary, getSensorStatus } from './dataLoader';

export const loadFullDataset = async () => {
  try {
    // Try to load real dataset first
    const realData = await loadRealDataset();
    if (realData) {
      return realData;
    }
  } catch (error) {
    console.warn('Failed to load real dataset, using fallback data');
  }
  
  // Fallback to mock data structure
  return {
    campaigns: mockCampaigns,
    sensors: mockSensorData,
    summary: {
      total_campaigns: 500,
      total_metrics: 46701,
      total_assets: 4427,
      active_sensors: 5,
      model_accuracy: 0.87
    }
  };
};

export const getDashboardMetrics = () => {
  try {
    return getDashboardSummary();
  } catch (error) {
    console.warn('Failed to get real dashboard metrics, using fallback');
    return {
      totalCampaigns: 500,
      activeCampaigns: 127,
      avgROI: 4.2,
      avgEngagement: 7.8,
      pipelineHealth: 95,
      dataFreshness: 98,
      modelAccuracy: 87,
      systemLatency: 145
    };
  }
};

export const getSensorMetrics = () => {
  try {
    const sensors = getSensorStatus();
    return {
      sensors: sensors.length > 0 ? sensors : [
        { name: "Data Freshness", value: 98, status: "OK", trend: "+2%" },
        { name: "Model Accuracy", value: 87, status: "OK", trend: "+1%" },
        { name: "API Latency", value: 145, status: "OK", trend: "-5ms" },
        { name: "Data Quality", value: 96, status: "OK", trend: "+3%" },
        { name: "Throughput", value: 1150, status: "OK", trend: "+8%" }
      ],
      alerts: [
        { id: 1, message: "High latency detected in EU region", severity: "warning", timestamp: "2024-06-08T20:15:00Z" },
        { id: 2, message: "Model retrained successfully", severity: "info", timestamp: "2024-06-08T18:30:00Z" }
      ]
    };
  } catch (error) {
    console.warn('Failed to get real sensor metrics, using fallback');
    return {
      sensors: [
        { name: "Data Freshness", value: 98, status: "OK", trend: "+2%" },
        { name: "Model Accuracy", value: 87, status: "OK", trend: "+1%" },
        { name: "API Latency", value: 145, status: "OK", trend: "-5ms" },
        { name: "Data Quality", value: 96, status: "OK", trend: "+3%" },
        { name: "Throughput", value: 1150, status: "OK", trend: "+8%" }
      ],
      alerts: [
        { id: 1, message: "High latency detected in EU region", severity: "warning", timestamp: "2024-06-08T20:15:00Z" },
        { id: 2, message: "Model retrained successfully", severity: "info", timestamp: "2024-06-08T18:30:00Z" }
      ]
    };
  }
};