import { motion } from "framer-motion";
import { Copy, Calendar, Download, RefreshCw, Star, Globe, ThumbsUp, MessageCircle, Repeat2, Send, Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useGenerationStore, WriterOutput, OptimizerOutput } from "@/stores/generationStore";

interface ReviewStepProps {
  onStartOver: () => void;
  // Optional props for history view
  writerOutput?: WriterOutput;
  optimizerOutput?: OptimizerOutput;
  selectedHookIndex?: number;
}

export function ReviewStep({ 
  onStartOver,
  writerOutput: propWriterOutput,
  optimizerOutput: propOptimizerOutput,
  selectedHookIndex: propSelectedHookIndex 
}: ReviewStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const writerOutput = propWriterOutput ?? store.writerOutput;
  const optimizerOutput = propOptimizerOutput ?? store.optimizerOutput;
  const selectedHookIndex = propSelectedHookIndex ?? store.selectedHookIndex;
  const setSelectedHookIndex = store.setSelectedHookIndex;
  
  if (!writerOutput || !optimizerOutput) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">No content available.</p>
      </div>
    );
  }
  
  const selectedHook = writerOutput.hooks[selectedHookIndex];
  const fullPost = `${selectedHook.text}\n\n${writerOutput.body_content}\n\n${writerOutput.cta}\n\n${writerOutput.hashtags.map(t => `#${t}`).join(" ")}`;
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(fullPost);
    toast.success("Post copied to clipboard!");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-2 gap-6"
    >
      {/* Left Column - Controls & Metrics */}
      <div className="space-y-4">
        {/* Success Banner */}
        <Card className="p-4 border-success/30 bg-success/5">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-success flex items-center justify-center text-success-foreground">
              <Check className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-semibold text-success">Your Post is Ready</h2>
              <p className="text-sm text-muted-foreground">
                All AI agents have completed their work
              </p>
            </div>
          </div>
        </Card>
        
        {/* Hook Selection */}
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Select Hook</h3>
          <div className="space-y-2">
            {writerOutput.hooks.map((hook, index) => (
              <div
                key={hook.version}
                onClick={() => setSelectedHookIndex(index)}
                className={cn(
                  "p-3 rounded-md border cursor-pointer transition-colors",
                  selectedHookIndex === index
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50"
                )}
              >
                <div className="flex items-start gap-2">
                  <div className={cn(
                    "h-5 w-5 rounded flex items-center justify-center text-xs font-medium shrink-0",
                    selectedHookIndex === index 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted"
                  )}>
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm line-clamp-2">{hook.text}</p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <Badge variant="secondary" className="text-xs capitalize">
                        {hook.hook_type.replace(/_/g, " ")}
                      </Badge>
                      <span className="flex items-center gap-1 text-warning text-xs font-mono">
                        <Star className="h-3 w-3 fill-warning" />
                        {hook.score.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
        
        {/* Quality Scores */}
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Quality Analysis</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Overall Score</span>
                <span className="font-mono">{optimizerOutput.quality_score.toFixed(1)}/10</span>
              </div>
              <Progress value={optimizerOutput.quality_score * 10} className="h-1.5" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Hook Strength</span>
                <span className="font-mono">{selectedHook.score.toFixed(1)}/10</span>
              </div>
              <Progress value={selectedHook.score * 10} className="h-1.5" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Brand Consistency</span>
                <span className="font-mono">{optimizerOutput.brand_consistency_score.toFixed(1)}/10</span>
              </div>
              <Progress value={optimizerOutput.brand_consistency_score * 10} className="h-1.5" />
            </div>
          </div>
        </Card>
        
        {/* Predicted Performance */}
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Predicted Performance</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 rounded-md bg-muted/30">
              <div className="text-lg font-semibold font-mono">
                {(optimizerOutput.predicted_impressions_min / 1000).toFixed(0)}K - {(optimizerOutput.predicted_impressions_max / 1000).toFixed(0)}K
              </div>
              <div className="text-xs text-muted-foreground">Impressions</div>
            </div>
            <div className="text-center p-3 rounded-md bg-muted/30">
              <div className="text-lg font-semibold font-mono">
                {optimizerOutput.predicted_engagement_rate.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">Engagement Rate</div>
            </div>
          </div>
        </Card>
        
        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Button onClick={copyToClipboard} className="gap-2">
            <Copy className="h-4 w-4" /> Copy Post
          </Button>
          <Button variant="outline" className="gap-2">
            <Calendar className="h-4 w-4" /> Schedule
          </Button>
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" /> Export
          </Button>
          <Button variant="ghost" onClick={onStartOver} className="gap-2">
            <RefreshCw className="h-4 w-4" /> Start Over
          </Button>
        </div>
      </div>
      
      {/* Right Column - LinkedIn Preview */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-muted-foreground">LinkedIn Preview</h3>
        
        <Card className="overflow-hidden">
          {/* Profile Header */}
          <div className="p-4 border-b flex items-center gap-3">
            <div className="h-11 w-11 rounded-full bg-gradient-to-br from-primary/80 to-primary" />
            <div className="flex-1">
              <div className="font-medium text-sm">Your Name</div>
              <div className="text-xs text-muted-foreground flex items-center gap-1">
                Your Title • Just now • <Globe className="h-3 w-3" />
              </div>
            </div>
          </div>
          
          {/* Post Content */}
          <div className="p-4 max-h-[420px] overflow-y-auto scrollbar-thin">
            <div className="whitespace-pre-line text-sm leading-relaxed">
              <span className="font-medium">{selectedHook.text}</span>
              {"\n\n"}
              {writerOutput.body_content}
              {"\n\n"}
              <span className="font-medium">{writerOutput.cta}</span>
              {"\n\n"}
              <span className="text-primary text-sm">
                {writerOutput.hashtags.map(t => `#${t}`).join(" ")}
              </span>
            </div>
          </div>
          
          {/* Engagement Bar */}
          <div className="px-4 py-2 border-t">
            <div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
              <span>👍 12</span>
              <span>3 comments</span>
            </div>
            <div className="flex items-center justify-between border-t pt-2 text-xs">
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-muted transition-colors">
                <ThumbsUp className="h-4 w-4" /> Like
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-muted transition-colors">
                <MessageCircle className="h-4 w-4" /> Comment
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-muted transition-colors">
                <Repeat2 className="h-4 w-4" /> Repost
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 rounded hover:bg-muted transition-colors">
                <Send className="h-4 w-4" /> Send
              </button>
            </div>
          </div>
        </Card>
        
        {/* Post Stats */}
        <Card className="p-3">
          <div className="grid grid-cols-3 gap-3 text-center text-sm">
            <div>
              <div className="font-mono font-medium">{writerOutput.formatting_metadata.word_count}</div>
              <div className="text-xs text-muted-foreground">Words</div>
            </div>
            <div>
              <div className="font-mono font-medium">{writerOutput.formatting_metadata.line_count}</div>
              <div className="text-xs text-muted-foreground">Lines</div>
            </div>
            <div>
              <div className="font-mono font-medium">{writerOutput.formatting_metadata.reading_time_seconds}s</div>
              <div className="text-xs text-muted-foreground">Read Time</div>
            </div>
          </div>
        </Card>
      </div>
    </motion.div>
  );
}
