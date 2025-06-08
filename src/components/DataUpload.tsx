
import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, Image, Video, Music, X, Check, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: "uploading" | "processing" | "completed" | "error";
  progress: number;
  metadata?: {
    campaign: string;
    category: string;
    objective: string;
    features?: string[];
  };
}

const DataUpload = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [campaignName, setCampaignName] = useState("");
  const [campaignCategory, setCampaignCategory] = useState("");
  const [campaignObjective, setCampaignObjective] = useState("");
  const [notes, setNotes] = useState("");
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFiles = (fileList: File[]) => {
    const newFiles: UploadedFile[] = fileList.map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: "uploading",
      progress: 0,
      metadata: {
        campaign: campaignName,
        category: campaignCategory,
        objective: campaignObjective
      }
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate upload and processing
    newFiles.forEach(file => {
      simulateUpload(file.id);
    });
  };

  const simulateUpload = (fileId: string) => {
    const interval = setInterval(() => {
      setFiles(prev => prev.map(file => {
        if (file.id === fileId) {
          if (file.progress < 100) {
            return { ...file, progress: file.progress + 10 };
          } else if (file.status === "uploading") {
            return { ...file, status: "processing" };
          } else if (file.status === "processing") {
            clearInterval(interval);
            // Simulate feature extraction
            setTimeout(() => {
              setFiles(prev => prev.map(f => 
                f.id === fileId 
                  ? { 
                      ...f, 
                      status: "completed",
                      metadata: {
                        ...f.metadata!,
                        features: ["Visual Appeal: 0.85", "Message Clarity: 0.72", "Brand Integration: 0.68"]
                      }
                    }
                  : f
              ));
            }, 2000);
          }
        }
        return file;
      }));
    }, 300);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return <Image className="h-5 w-5" />;
    if (type.startsWith("video/")) return <Video className="h-5 w-5" />;
    if (type.startsWith("audio/")) return <Music className="h-5 w-5" />;
    return <FileText className="h-5 w-5" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "uploading": return "bg-blue-500";
      case "processing": return "bg-yellow-500";
      case "completed": return "bg-green-500";
      case "error": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Campaign Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Campaign Information</CardTitle>
          <CardDescription>
            Provide context for the assets you're uploading
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="campaign-name">Campaign Name</Label>
              <Input
                id="campaign-name"
                placeholder="e.g., Summer 2024 Launch"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select value={campaignCategory} onValueChange={setCampaignCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="automotive">Automotive</SelectItem>
                  <SelectItem value="fmcg">FMCG</SelectItem>
                  <SelectItem value="tech">Technology</SelectItem>
                  <SelectItem value="fashion">Fashion</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="food">Food & Beverage</SelectItem>
                  <SelectItem value="healthcare">Healthcare</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="objective">Primary Objective</Label>
              <Select value={campaignObjective} onValueChange={setCampaignObjective}>
                <SelectTrigger>
                  <SelectValue placeholder="Select objective" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="awareness">Brand Awareness</SelectItem>
                  <SelectItem value="consideration">Consideration</SelectItem>
                  <SelectItem value="conversion">Conversion</SelectItem>
                  <SelectItem value="retention">Retention</SelectItem>
                  <SelectItem value="advocacy">Advocacy</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea
              id="notes"
              placeholder="Any additional context about this campaign..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Creative Assets
          </CardTitle>
          <CardDescription>
            Drop files here or click to browse. Supports images, videos, audio, and documents.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? "border-primary bg-primary/5" 
                : "border-muted-foreground/25 hover:border-muted-foreground/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <div className="space-y-2">
              <p className="text-lg font-medium">Drop files here</p>
              <p className="text-sm text-muted-foreground">
                or{" "}
                <label className="text-primary cursor-pointer hover:underline">
                  browse your computer
                  <input
                    type="file"
                    multiple
                    className="hidden"
                    onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
                    accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.ppt,.pptx"
                  />
                </label>
              </p>
              <p className="text-xs text-muted-foreground">
                Supports: Images, Videos, Audio, PDF, Word, PowerPoint
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Processing Queue</CardTitle>
            <CardDescription>
              Track the upload and analysis progress of your files
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {files.map((file) => (
                <div key={file.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {getFileIcon(file.type)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{file.name}</span>
                          <Badge variant="outline" className="text-xs">
                            {formatFileSize(file.size)}
                          </Badge>
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(file.status)}`} />
                        </div>
                        
                        <div className="text-sm text-muted-foreground mb-2">
                          Status: {file.status === "uploading" && "Uploading..."}
                          {file.status === "processing" && "Extracting features..."}
                          {file.status === "completed" && "Analysis complete"}
                          {file.status === "error" && "Processing failed"}
                        </div>

                        {(file.status === "uploading" || file.status === "processing") && (
                          <Progress value={file.progress} className="w-full h-2 mb-2" />
                        )}

                        {file.metadata && (
                          <div className="flex flex-wrap gap-1 mb-2">
                            {file.metadata.campaign && (
                              <Badge variant="secondary" className="text-xs">
                                {file.metadata.campaign}
                              </Badge>
                            )}
                            {file.metadata.category && (
                              <Badge variant="secondary" className="text-xs">
                                {file.metadata.category}
                              </Badge>
                            )}
                            {file.metadata.objective && (
                              <Badge variant="secondary" className="text-xs">
                                {file.metadata.objective}
                              </Badge>
                            )}
                          </div>
                        )}

                        {file.metadata?.features && (
                          <div className="mt-2">
                            <div className="text-xs font-medium mb-1">Extracted Features:</div>
                            <div className="flex flex-wrap gap-1">
                              {file.metadata.features.map((feature, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {feature}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {file.status === "completed" && (
                        <Check className="h-4 w-4 text-green-500" />
                      )}
                      {file.status === "error" && (
                        <AlertCircle className="h-4 w-4 text-red-500" />
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeFile(file.id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {files.some(f => f.status === "completed") && (
              <div className="mt-4 pt-4 border-t">
                <Button className="w-full">
                  Process All Completed Files
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Processing Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Files Uploaded</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{files.length}</div>
            <p className="text-xs text-muted-foreground">
              {files.filter(f => f.status === "completed").length} processed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Size</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}
            </div>
            <p className="text-xs text-muted-foreground">across all files</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Features Extracted</CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {files.reduce((sum, f) => sum + (f.metadata?.features?.length || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">creative features</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <Check className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {files.length > 0 
                ? Math.round((files.filter(f => f.status === "completed").length / files.length) * 100)
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">processing success</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DataUpload;
