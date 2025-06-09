import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Chart } from "@/components/charts/Chart";
import { Metric } from "@/components/metrics/Metric";

interface QueryResponse {
  answer: string;
  sql?: string;
  charts: Array<{
    id: string;
    title: string;
    type: string;
    data_source: string;
    x_axis: string;
    y_axis: string;
  }>;
  metrics: Array<{
    id: string;
    name: string;
    value: number;
    type: string;
  }>;
  raw_data?: any;
  timestamp: string;
}

export function AskCes() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: query,
          time_range: "month",
          top_k: 5
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to get response");
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Query Input */}
      <Card>
        <CardHeader>
          <CardTitle>Ask CES</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              placeholder="Ask CES about campaign effectiveness..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Thinking...
                </>
              ) : (
                "Ask"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Error Message */}
      {error && (
        <Card className="bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Response */}
      {response && (
        <div className="space-y-6">
          {/* Narrative Answer */}
          <Card>
            <CardContent className="pt-6">
              <p className="text-lg whitespace-pre-line">{response.answer}</p>
            </CardContent>
          </Card>

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {response.metrics.map((metric) => (
              <Metric
                key={metric.id}
                title={metric.name}
                value={metric.value}
                type={metric.type}
              />
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {response.charts.map((chart) => (
              <Card key={chart.id}>
                <CardHeader>
                  <CardTitle>{chart.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <Chart
                    type={chart.type}
                    data={response.raw_data?.[chart.data_source] || []}
                    xAxis={chart.x_axis}
                    yAxis={chart.y_axis}
                  />
                </CardContent>
              </Card>
            ))}
          </div>

          {/* SQL Query (Collapsible) */}
          {response.sql && (
            <Card>
              <CardHeader>
                <CardTitle>Generated SQL</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                  <code>{response.sql}</code>
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
} 