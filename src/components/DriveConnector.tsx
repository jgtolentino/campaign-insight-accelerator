
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Folder, File, Download, Eye, Tag, Calendar } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime: string;
  size?: string;
  webViewLink?: string;
}

const DriveConnector = () => {
  const [folderId, setFolderId] = useState("");
  const [files, setFiles] = useState<DriveFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const { toast } = useToast();

  // Mock data for demonstration
  const mockFiles: DriveFile[] = [
    {
      id: "1",
      name: "2024_Q1_Campaign_Analysis.pdf",
      mimeType: "application/pdf",
      modifiedTime: "2024-03-15T10:30:00Z",
      size: "2.4 MB"
    },
    {
      id: "2", 
      name: "Brand_Sentiment_Report_March.xlsx",
      mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      modifiedTime: "2024-03-10T14:20:00Z",
      size: "1.8 MB"
    },
    {
      id: "3",
      name: "Creative_Assets_2024",
      mimeType: "application/vnd.google-apps.folder",
      modifiedTime: "2024-03-12T09:15:00Z"
    },
    {
      id: "4",
      name: "Video_Performance_Data.json",
      mimeType: "application/json", 
      modifiedTime: "2024-03-14T16:45:00Z",
      size: "856 KB"
    }
  ];

  const handleConnect = async () => {
    if (!folderId.trim()) {
      toast({
        title: "Error",
        description: "Please enter a valid Google Drive folder ID",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setFiles(mockFiles);
      setConnected(true);
      setLoading(false);
      toast({
        title: "Connected",
        description: `Successfully connected to Drive folder`
      });
    }, 2000);
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.includes("folder")) return <Folder className="h-4 w-4 text-blue-500" />;
    return <File className="h-4 w-4 text-gray-500" />;
  };

  const getFileType = (mimeType: string) => {
    if (mimeType.includes("pdf")) return "PDF";
    if (mimeType.includes("spreadsheet")) return "Excel";
    if (mimeType.includes("folder")) return "Folder";
    if (mimeType.includes("json")) return "JSON";
    return "File";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short", 
      day: "numeric"
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Folder className="h-5 w-5" />
            Google Drive Archive Connection
          </CardTitle>
          <CardDescription>
            Connect to your campaign archive folder to access and analyze creative assets
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="folderId">Drive Folder ID</Label>
            <Input
              id="folderId"
              placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
              value={folderId}
              onChange={(e) => setFolderId(e.target.value)}
              disabled={connected}
            />
            <p className="text-xs text-muted-foreground">
              Find the folder ID in your Google Drive URL after /folders/
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button 
              onClick={handleConnect} 
              disabled={loading || connected}
              className="flex items-center gap-2"
            >
              {loading ? "Connecting..." : connected ? "Connected" : "Connect to Drive"}
            </Button>
            {connected && (
              <Button 
                variant="outline" 
                onClick={() => {
                  setConnected(false);
                  setFiles([]);
                  setFolderId("");
                }}
              >
                Disconnect
              </Button>
            )}
          </div>

          {connected && (
            <div className="pt-4 border-t">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium">Campaign Archive Files</h3>
                <Badge variant="secondary">{files.length} files</Badge>
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {files.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50">
                    <div className="flex items-center gap-3">
                      {getFileIcon(file.mimeType)}
                      <div>
                        <p className="font-medium text-sm">{file.name}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Badge variant="outline" className="text-xs">
                            {getFileType(file.mimeType)}
                          </Badge>
                          {file.size && <span>{file.size}</span>}
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {formatDate(file.modifiedTime)}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" className="h-8">
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                      <Button size="sm" variant="outline" className="h-8">
                        <Tag className="h-3 w-3 mr-1" />
                        Tag
                      </Button>
                      <Button size="sm" variant="outline" className="h-8">
                        <Download className="h-3 w-3 mr-1" />
                        Process
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {connected && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Status</CardTitle>
            <CardDescription>
              Track the analysis progress of your campaign files
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">156</div>
                  <div className="text-sm text-muted-foreground">Files Processed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">89</div>
                  <div className="text-sm text-muted-foreground">Features Extracted</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">12</div>
                  <div className="text-sm text-muted-foreground">Models Trained</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DriveConnector;
