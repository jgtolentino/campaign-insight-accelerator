import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

// Get JWT token from Supabase auth
const getAuthToken = async () => {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token;
};

// Base API client with tenant-aware headers
const apiClient = {
  async fetch(endpoint: string, options: RequestInit = {}) {
    const token = await getAuthToken();
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(`${import.meta.env.VITE_API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }
};

export interface SensorStatus {
  name: string;
  status: 'OK' | 'FAIL';
  lastRun: string;
  metrics?: {
    accuracy: number;
    latency: number;
    throughput: number;
  };
}

export interface MetricHistory {
  timestamp: string;
  accuracy: number;
  latency: number;
  throughput: number;
}

export async function getSensors(): Promise<SensorStatus[]> {
  return apiClient.fetch('/api/sensors');
}

export async function getMetricHistory(): Promise<MetricHistory[]> {
  return apiClient.fetch('/api/metrics/history');
}

export async function triggerRetrain(): Promise<{ jobId: string }> {
  return apiClient.fetch('/api/retrain', {
    method: 'POST',
  });
}

export async function getModelStatus(): Promise<{
  status: string;
  lastTrained: string;
  metrics: {
    accuracy: number;
    latency: number;
    throughput: number;
  };
}> {
  return apiClient.fetch('/api/model/status');
}

export async function getRetrainingJobs(): Promise<{
  id: string;
  status: string;
  startedAt: string;
  completedAt: string | null;
  errorMessage: string | null;
}[]> {
  return apiClient.fetch('/api/retraining/jobs');
} 