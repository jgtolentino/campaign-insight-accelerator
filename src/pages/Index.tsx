
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Database, MessageSquare, Upload, TrendingUp, Brain } from "lucide-react";
import CampaignDashboard from "@/components/CampaignDashboard";
import DriveConnector from "@/components/DriveConnector";
import RAGInterface from "@/components/RAGInterface";
import DataUpload from "@/components/DataUpload";

const Index = () => {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">CES Model Rebuild</h1>
              <p className="text-muted-foreground mt-1">
                Ground-Up Approach to Campaign Effectiveness
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Brain className="h-8 w-8 text-primary" />
              <span className="text-sm text-muted-foreground">v2.0</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="drive" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              Drive Archive
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="rag" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Query Engine
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Data Upload
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Performance Focus
                  </CardTitle>
                  <CardDescription>
                    From award recognition to business impact
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Shifting from award-winning campaigns as proxy to performance-grounded, 
                    data-first strategy focusing on features that drive real business outcomes.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Feature Ranking
                  </CardTitle>
                  <CardDescription>
                    Creative elements by predictive power
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Analyze engagement, brand recall, conversion rates, ROI, sentiment, 
                    CAC, media efficiency, and long-term brand equity.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-primary" />
                    Explainable AI
                  </CardTitle>
                  <CardDescription>
                    Human-complementary insights
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Scalable ML models that remain explainable and complement 
                    human judgment in creative decision-making.
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Key Metrics Overview */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Business Outcomes Tracked</CardTitle>
                <CardDescription>
                  Comprehensive metrics for campaign effectiveness analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm text-primary">Engagement</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Views, Likes, Shares</li>
                      <li>• Completion Rate</li>
                      <li>• Time Spent</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm text-primary">Performance</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• CTR & Conversion Rate</li>
                      <li>• ROI & Sales Lift</li>
                      <li>• CAC & Lead Generation</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm text-primary">Brand Impact</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Brand Recall & Recognition</li>
                      <li>• Sentiment Analysis</li>
                      <li>• Long-term Brand Equity</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="drive" className="mt-6">
            <DriveConnector />
          </TabsContent>

          <TabsContent value="dashboard" className="mt-6">
            <CampaignDashboard />
          </TabsContent>

          <TabsContent value="rag" className="mt-6">
            <RAGInterface />
          </TabsContent>

          <TabsContent value="upload" className="mt-6">
            <DataUpload />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Index;
