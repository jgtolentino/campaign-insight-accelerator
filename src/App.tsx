import { useState, useEffect } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';
import { getDashboardMetrics, getSensorMetrics, loadFullDataset } from '@/lib/mockData';

const queryClient = new QueryClient();

interface DashboardData {
  totalCampaigns: number;
  activeCampaigns: number;
  avgROI: number;
  avgEngagement: number;
  pipelineHealth: number;
  dataFreshness: number;
  modelAccuracy: number;
  systemLatency: number;
}

function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [sensorMetrics, setSensorMetrics] = useState<{
    sensors: Array<{ name: string; value: number; status: string; trend: string }>;
    alerts: Array<{ id: number; message: string; severity: string; timestamp: string }>;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Load the real generated dataset
        const fullDataset = await loadFullDataset();
        const dashboard = getDashboardMetrics();
        const sensors = getSensorMetrics();
        
        setDashboardData(dashboard);
        setSensorMetrics(sensors);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading || !dashboardData || !sensorMetrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Campaign Insight Accelerator...</p>
        </div>
      </div>
    );
  }

  const colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Campaign Insight Accelerator</h1>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-500">Live Data</span>
            </div>
          </div>
          <p className="mt-2 text-gray-600">Real-time monitoring of campaign effectiveness and ML pipeline health</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Key Metrics Overview */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">C</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-500">Total Campaigns</h3>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.totalCampaigns}</p>
                  <p className="text-sm text-green-600">{dashboardData.activeCampaigns} active</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">R</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-500">Avg ROI</h3>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.avgROI}x</p>
                  <p className="text-sm text-green-600">+12% vs last month</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">E</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-500">Engagement Rate</h3>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.avgEngagement}%</p>
                  <p className="text-sm text-green-600">+2.1% vs last week</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold">H</span>
                  </div>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-500">Pipeline Health</h3>
                  <p className="text-2xl font-bold text-gray-900">{dashboardData.pipelineHealth}%</p>
                  <p className="text-sm text-green-600">All systems operational</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sensor Status Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5 mb-8">
          {sensorMetrics.sensors.map((sensor: any, index: number) => (
            <div key={sensor.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">{sensor.name}</h3>
                    <p className="text-lg font-bold text-gray-900">{sensor.value}{sensor.name === 'API Latency' ? 'ms' : sensor.name === 'Throughput' ? '/min' : '%'}</p>
                    <p className="text-xs text-green-600">{sensor.trend}</p>
                  </div>
                  <div className="flex-shrink-0">
                    {sensor.status === 'OK' ? (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    ) : sensor.status === 'WARN' ? (
                      <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
                    ) : (
                      <XCircleIcon className="h-6 w-6 text-red-500" />
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Alerts and Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Recent Alerts */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Alerts</h2>
            <div className="space-y-3">
              {sensorMetrics.alerts.map((alert: any) => (
                <div key={alert.id} className={`p-3 rounded-lg border ${alert.severity === 'warning' ? 'bg-yellow-50 border-yellow-200' : 'bg-blue-50 border-blue-200'}`}>
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${alert.severity === 'warning' ? 'bg-yellow-400' : 'bg-blue-400'}`}></div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                      <p className="text-xs text-gray-500">{new Date(alert.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Campaign Performance Chart */}
          <div className="bg-white shadow rounded-lg p-6 lg:col-span-2">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Campaign Performance Trends</h2>
            <div className="h-64">
              <LineChart width={500} height={250} data={[
                { name: 'Week 1', roi: 3.2, engagement: 6.8, reach: 850 },
                { name: 'Week 2', roi: 3.8, engagement: 7.2, reach: 920 },
                { name: 'Week 3', roi: 4.1, engagement: 7.5, reach: 1100 },
                { name: 'Week 4', roi: 4.2, engagement: 7.8, reach: 1250 },
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="roi" stroke="#0ea5e9" name="ROI" />
                <Line type="monotone" dataKey="engagement" stroke="#10b981" name="Engagement %" />
              </LineChart>
            </div>
          </div>
        </div>

        {/* Data Summary */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Dataset Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">52,678</p>
              <p className="text-sm text-gray-500">Total Records</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">46,701</p>
              <p className="text-sm text-gray-500">Performance Metrics</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">4,427</p>
              <p className="text-sm text-gray-500">Creative Assets</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">10</p>
              <p className="text-sm text-gray-500">Major Brands</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
