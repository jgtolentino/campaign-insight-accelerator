
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageSquare, Send, Brain, FileText, BarChart3, Lightbulb } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Array<{
    title: string;
    excerpt: string;
    relevance: number;
  }>;
}

const RAGInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content: "Hello! I'm your CES AI assistant. I can help you analyze campaign effectiveness, explore feature importance, and answer questions about your creative performance data. What would you like to know?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const suggestedQueries = [
    "What are the top 5 features that drive CTR?",
    "Show me campaigns with high emotional resonance scores",
    "How does brand integration impact conversion rates?",
    "What creative patterns work best for Gen Z audiences?",
    "Compare visual appeal across different product categories",
    "Which campaigns had the highest ROI last quarter?"
  ];

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: generateMockResponse(input),
        timestamp: new Date(),
        sources: [
          {
            title: "Q1 2024 Campaign Performance Report",
            excerpt: "Analysis of 156 campaigns showing visual appeal correlation with CTR...",
            relevance: 0.94
          },
          {
            title: "Brand Integration Study - TBWA Analytics",
            excerpt: "Cross-campaign analysis revealing optimal brand placement strategies...",
            relevance: 0.87
          },
          {
            title: "Emotional Resonance Framework v2.1",
            excerpt: "Updated methodology for measuring emotional impact in creative assets...",
            relevance: 0.82
          }
        ]
      };

      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 2000);
  };

  const generateMockResponse = (query: string): string => {
    if (query.toLowerCase().includes("ctr")) {
      return `Based on the analysis of 156 campaigns in our archive, the top 5 features that drive CTR are:

1. **Visual Appeal** (0.85 correlation) - Clean, eye-catching designs with strong visual hierarchy
2. **Message Clarity** (0.78 correlation) - Clear, concise copy that communicates value proposition
3. **Brand Integration** (0.72 correlation) - Seamless brand presence without being overly promotional
4. **Emotional Resonance** (0.68 correlation) - Content that evokes positive emotional responses
5. **Call to Action** (0.65 correlation) - Clear, compelling CTAs with action-oriented language

These insights are derived from SHAP analysis across multiple campaign types and audience segments. Would you like me to dive deeper into any specific feature?`;
    }

    if (query.toLowerCase().includes("emotional")) {
      return `Campaigns with high emotional resonance scores (>0.8) show several common patterns:

**Top Performing Elements:**
- Authentic human stories and testimonials
- Music that matches the emotional tone
- Color palettes that evoke desired feelings
- Pacing that allows emotional moments to resonate

**Performance Impact:**
- 23% higher engagement rates
- 15% better brand recall
- 18% improvement in purchase intent

**Recent Examples:**
- "Moments that Matter" campaign (ER: 0.91, CTR: 3.4%)
- "Real Stories" series (ER: 0.88, Conversion: 4.2%)

The data suggests emotional resonance is particularly effective for brand awareness objectives rather than direct response campaigns.`;
    }

    return `I've analyzed your query and found relevant insights from our campaign effectiveness database. The patterns show interesting correlations between creative features and business outcomes. Here are the key findings:

- Feature importance varies by campaign objective and audience segment
- Cross-channel performance requires different optimization strategies  
- Temporal factors (seasonality, timing) significantly impact effectiveness

Would you like me to provide more specific data points or explore a particular aspect in greater detail?`;
  };

  const handleSuggestedQuery = (query: string) => {
    setInput(query);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            CES RAG Query Engine
          </CardTitle>
          <CardDescription>
            Ask questions about campaign effectiveness, feature importance, and creative performance insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Suggested Queries */}
          <div className="mb-6">
            <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Suggested Queries
            </h4>
            <div className="flex flex-wrap gap-2">
              {suggestedQueries.map((query, index) => (
                <Badge 
                  key={index}
                  variant="outline" 
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                  onClick={() => handleSuggestedQuery(query)}
                >
                  {query}
                </Badge>
              ))}
            </div>
          </div>

          {/* Chat Messages */}
          <ScrollArea className="h-96 border rounded-lg p-4 mb-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] rounded-lg p-3 ${
                    message.type === "user" 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted"
                  }`}>
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                    
                    {message.sources && (
                      <div className="mt-3 pt-3 border-t border-border/20">
                        <div className="text-xs font-medium mb-2 flex items-center gap-1">
                          <FileText className="h-3 w-3" />
                          Sources ({message.sources.length})
                        </div>
                        <div className="space-y-2">
                          {message.sources.map((source, index) => (
                            <div key={index} className="text-xs bg-background/50 rounded p-2">
                              <div className="font-medium">{source.title}</div>
                              <div className="text-muted-foreground mt-1">{source.excerpt}</div>
                              <div className="mt-1">
                                <Badge variant="outline" className="text-xs">
                                  {(source.relevance * 100).toFixed(0)}% relevant
                                </Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center gap-2 text-sm">
                      <Brain className="h-4 w-4 animate-pulse" />
                      Analyzing campaign data...
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Ask about campaign effectiveness, feature importance, or creative insights..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={loading}
            />
            <Button onClick={handleSendMessage} disabled={loading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Query Analytics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Queries Today</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">47</div>
            <p className="text-xs text-muted-foreground">+12% from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2s</div>
            <p className="text-xs text-muted-foreground">-0.3s improvement</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Base</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-muted-foreground">documents indexed</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RAGInterface;
