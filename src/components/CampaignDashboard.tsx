
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, ScatterChart, Scatter, Cell } from "recharts";
import { TrendingUp, TrendingDown, Target, Eye, Heart, MousePointer } from "lucide-react";

const CampaignDashboard = () => {
  const [selectedMetric, setSelectedMetric] = useState("ctr");
  const [selectedTimeframe, setSelectedTimeframe] = useState("last30");

  // Mock data for feature importance
  const featureImportanceData = [
    { feature: "Visual Appeal", importance: 0.85, change: +0.12 },
    { feature: "Message Clarity", importance: 0.78, change: +0.08 },
    { feature: "Brand Integration", importance: 0.72, change: -0.05 },
    { feature: "Emotional Resonance", importance: 0.68, change: +0.15 },
    { feature: "Call to Action", importance: 0.65, change: +0.03 },
    { feature: "Color Palette", importance: 0.58, change: -0.02 },
    { feature: "Audio Quality", importance: 0.52, change: +0.07 },
    { feature: "Pacing", importance: 0.48, change: -0.08 }
  ];

  // Mock campaign performance data
  const campaignPerformance = [
    { name: "Week 1", ctr: 2.4, engagement: 8.2, conversion: 3.1 },
    { name: "Week 2", ctr: 2.8, engagement: 9.1, conversion: 3.4 },
    { name: "Week 3", ctr: 3.2, engagement: 10.5, conversion: 4.2 },
    { name: "Week 4", ctr: 2.9, engagement: 9.8, conversion: 3.8 }
  ];

  // Mock feature correlation data
  const featureCorrelation = [
    { feature: "Visual Appeal", metric: 0.85, campaigns: 45 },
    { feature: "Message Clarity", metric: 0.78, campaigns: 52 },
    { feature: "Brand Integration", metric: 0.72, campaigns: 38 },
    { feature: "Emotional Resonance", metric: 0.68, campaigns: 41 },
    { feature: "Call to Action", metric: 0.65, campaigns: 49 },
    { feature: "Color Palette", metric: 0.58, campaigns: 35 },
    { feature: "Audio Quality", metric: 0.52, campaigns: 28 },
    { feature: "Pacing", metric: 0.48, campaigns: 33 }
  ];

  const getMetricIcon = (metric: string) => {
    switch (metric) {
      case "ctr": return <MousePointer className="h-4 w-4" />;
      case "engagement": return <Heart className="h-4 w-4" />;
      case "conversion": return <Target className="h-4 w-4" />;
      default: return <Eye className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="space-y-2">
          <label className="text-sm font-medium">Primary Metric</label>
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ctr">Click-Through Rate</SelectItem>
              <SelectItem value="engagement">Engagement Rate</SelectItem>
              <SelectItem value="conversion">Conversion Rate</SelectItem>
              <SelectItem value="roi">Return on Investment</SelectItem>
              <SelectItem value="sentiment">Brand Sentiment</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Timeframe</label>
          <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="last7">Last 7 days</SelectItem>
              <SelectItem value="last30">Last 30 days</SelectItem>
              <SelectItem value="last90">Last 90 days</SelectItem>
              <SelectItem value="last365">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg CTR</CardTitle>
            <MousePointer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.8%</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              +0.4% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">9.4%</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              +1.2% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3.6%</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <TrendingDown className="h-3 w-3 text-red-500" />
              -0.2% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CES Score</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">82.3</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              +3.1 from last period
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Feature Importance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Feature Importance for {selectedMetric.toUpperCase()}</CardTitle>
            <CardDescription>
              SHAP values showing which creative features most impact performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={featureImportanceData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 1]} />
                <YAxis dataKey="feature" type="category" width={100} />
                <Tooltip 
                  formatter={(value, name) => [
                    `${(value as number * 100).toFixed(1)}%`, 
                    'Importance'
                  ]}
                />
                <Bar dataKey="importance" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Trend</CardTitle>
            <CardDescription>
              Campaign metrics over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={campaignPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey={selectedMetric} 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ fill: "#8884d8" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Feature Correlation Scatter */}
      <Card>
        <CardHeader>
          <CardTitle>Feature vs Performance Correlation</CardTitle>
          <CardDescription>
            Relationship between creative features and business outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={featureCorrelation}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" name="Feature Score" />
              <YAxis dataKey="campaigns" name="Campaign Count" />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-background border rounded p-2 shadow-md">
                        <p className="font-medium">{data.feature}</p>
                        <p className="text-sm">Score: {data.metric}</p>
                        <p className="text-sm">Campaigns: {data.campaigns}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter dataKey="metric" fill="#8884d8">
                {featureCorrelation.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`hsl(${index * 45}, 70%, 50%)`} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Feature Changes */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Impact Changes</CardTitle>
          <CardDescription>
            How feature importance has evolved over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {featureImportanceData.map((feature, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <div className="font-medium">{feature.feature}</div>
                  <Badge variant="outline">
                    {(feature.importance * 100).toFixed(1)}% importance
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  {feature.change > 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-sm ${feature.change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {feature.change > 0 ? '+' : ''}{(feature.change * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CampaignDashboard;
