import { motion } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Search,
  Plus,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronRight,
  Sparkles,
  Target,
  Pen,
  Zap,
  FileText,
  Images,
  Calendar,
  RefreshCcw,
} from "lucide-react";
import { getHistoryList, GenerationHistoryListItem } from "@/services/api";

// Helper to map API status to agent completion count
const getAgentCounts = (status: string): { completed: number; total: number } => {
  const total = 5; // validator, strategist, writer, visual, optimizer
  switch (status) {
    case "completed":
      return { completed: 5, total };
    case "awaiting_answers":
      return { completed: 2, total }; // validator + strategist done
    case "processing":
      return { completed: 2, total }; // assume in progress after questions
    case "rejected":
      return { completed: 1, total }; // only validator ran
    case "failed":
      return { completed: 2, total };
    default:
      return { completed: 0, total };
  }
};

// Helper to estimate word count from final post
const estimateWordCount = (history: GenerationHistoryListItem): number => {
  return 350; // Default estimate, can be calculated from writer_output if available
};

const agentSteps = [
  { name: "Validator", icon: Sparkles },
  { name: "Strategist", icon: Target },
  { name: "Writer", icon: Pen },
  { name: "Optimizer", icon: Zap },
  { name: "Review", icon: CheckCircle },
];


const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(date);
};

const formatFullDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", { 
    month: "short", 
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
};

const getStatusConfig = (status: string) => {
  switch (status) {
    case "completed":
      return { icon: CheckCircle, color: "text-success", bg: "bg-success/10", border: "border-success/20", label: "Completed" };
    case "processing":
      return { icon: Loader2, color: "text-primary", bg: "bg-primary/10", border: "border-primary/20", label: "Processing", animate: true };
    case "failed":
      return { icon: AlertCircle, color: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/20", label: "Failed" };
    default:
      return { icon: Clock, color: "text-muted-foreground", bg: "bg-muted", border: "border-border", label: status };
  }
};

const getFormatConfig = (format: string) => {
  switch (format) {
    case "carousel":
      return { icon: Images, label: "Carousel Post", color: "text-violet-600 dark:text-violet-400" };
    case "text":
    default:
      return { icon: FileText, label: "Text Post", color: "text-blue-600 dark:text-blue-400" };
  }
};

export default function GenerationHistoryPage() {
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch generation history from API
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['generationHistory'],
    queryFn: () => getHistoryList(50, 0),
    staleTime: 30000, // 30 seconds
  });

  // Map API response to UI format and filter by search
  const generations = (data?.histories || []).map((h) => {
    const agentCounts = getAgentCounts(h.status);
    return {
      id: h.history_id,
      raw_idea: h.raw_idea,
      status: h.status,
      format: h.format || "text",
      quality_score: h.quality_score,
      created_at: h.started_at,
      agents_completed: agentCounts.completed,
      total_agents: agentCounts.total,
      word_count: estimateWordCount(h),
      estimated_read_time: h.status === "completed" ? "2 min" : "-",
    };
  });

  const filteredGenerations = generations.filter((gen) =>
    gen.raw_idea.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-40" />
        </div>

        {/* Search Skeleton */}
        <Card className="p-4">
          <Skeleton className="h-9 w-full rounded-md" />
        </Card>

        {/* List Skeleton */}
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
             <Card key={i} className="overflow-hidden border-l-4 border-l-muted">
                <div className="p-5">
                   <div className="flex justify-between mb-3">
                      <div className="flex gap-3">
                         <Skeleton className="h-6 w-24 rounded-full" />
                         <Skeleton className="h-6 w-20" />
                      </div>
                      <Skeleton className="h-6 w-24" />
                   </div>
                   <Skeleton className="h-7 w-3/4 mb-4" />
                   <div className="space-y-2">
                      <div className="flex justify-between">
                         <Skeleton className="h-3 w-32" />
                         <Skeleton className="h-3 w-24" />
                      </div>
                      <Skeleton className="h-2 w-full rounded-full" />
                      <div className="flex justify-between mt-3 pt-3 border-t border-border/50">
                          {Array.from({ length: 5 }).map((_, s) => (
                             <div key={s} className="flex flex-col items-center gap-1.5 flex-1">
                                <Skeleton className="h-8 w-8 rounded-lg" />
                                <Skeleton className="h-2 w-10" />
                             </div>
                          ))}
                      </div>
                   </div>
                </div>
                <div className="px-5 py-3 bg-muted/30 border-t border-border/50">
                    <Skeleton className="h-4 w-48" />
                </div>
             </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Card className="p-8 text-center">
          <AlertCircle className="h-10 w-10 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Failed to load history</h3>
          <p className="text-muted-foreground mb-4">
            {(error as Error).message || "Could not connect to the server"}
          </p>
          <Button onClick={() => refetch()}>
            <RefreshCcw className="mr-2 h-4 w-4" /> Try Again
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Generation History</h1>
          <p className="text-muted-foreground mt-1">
            View all your AI post generation runs and their agent outputs
          </p>
        </div>
        <Link to="/app/generate">
          <Button>
            <Plus className="mr-2 h-4 w-4" /> New Generation
          </Button>
        </Link>
      </div>

      {/* Search */}
      <Card className="p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by idea or topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </Card>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        Showing {filteredGenerations.length} generation{filteredGenerations.length !== 1 && "s"}
      </div>

      {/* Generation List */}
      <div className="grid gap-4">
        {filteredGenerations.map((gen, index) => {
          const statusConfig = getStatusConfig(gen.status);
          const formatConfig = getFormatConfig(gen.format);
          const StatusIcon = statusConfig.icon;
          const FormatIcon = formatConfig.icon;
          const progressPercent = (gen.agents_completed / gen.total_agents) * 100;

          return (
            <motion.div
              key={gen.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link to={`/app/generations/${gen.id}`}>

                <Card className={`overflow-hidden hover:shadow-lg transition-all cursor-pointer group border-l-4 ${statusConfig.border}`}>
                  {/* Main Content */}
                  <div className="p-5">
                    {/* Top Row: Status, Format, Date */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {/* Status Badge */}
                        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${statusConfig.bg}`}>
                          <StatusIcon className={`h-3.5 w-3.5 ${statusConfig.color} ${statusConfig.animate ? "animate-spin" : ""}`} />
                          <span className={`text-xs font-medium ${statusConfig.color}`}>
                            {statusConfig.label}
                          </span>
                        </div>
                        
                        {/* Format Badge */}
                        <div className="flex items-center gap-1.5 text-muted-foreground">
                          <FormatIcon className={`h-3.5 w-3.5 ${formatConfig.color}`} />
                          <span className="text-xs">{formatConfig.label}</span>
                        </div>
                      </div>

                      {/* Date & Score */}
                      <div className="flex items-center gap-3">
                        {gen.quality_score && (
                          <div className="flex items-center gap-1 bg-success/10 text-success px-2.5 py-1 rounded-full">
                            <Sparkles className="h-3 w-3" />
                            <span className="text-xs font-semibold">{gen.quality_score}/10</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {formatFullDate(gen.created_at)}
                        </div>
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="font-semibold text-lg text-foreground group-hover:text-primary transition-colors mb-4 line-clamp-2">
                      {gen.raw_idea}
                    </h3>

                    {/* Agent Pipeline Progress */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Agent Pipeline Progress</span>
                        <span className="font-medium">{gen.agents_completed} of {gen.total_agents} completed</span>
                      </div>
                      
                      {/* Progress Bar */}
                      <Progress value={progressPercent} className="h-2" />
                      
                      {/* Agent Steps */}
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/50">
                        {agentSteps.map((step, i) => {
                          const StepIcon = step.icon;
                          const isCompleted = i < gen.agents_completed;
                          const isCurrent = i === gen.agents_completed && gen.status === "processing";
                          
                          return (
                            <div key={step.name} className="flex flex-col items-center gap-1.5 flex-1">
                              <div
                                className={`h-8 w-8 rounded-lg flex items-center justify-center transition-all ${
                                  isCompleted
                                    ? "bg-success/15 text-success"
                                    : isCurrent
                                    ? "bg-primary/15 text-primary animate-pulse"
                                    : "bg-muted text-muted-foreground/40"
                                }`}
                              >
                                <StepIcon className={`h-4 w-4 ${isCurrent ? "animate-spin" : ""}`} />
                              </div>
                              <span className={`text-[10px] font-medium ${
                                isCompleted 
                                  ? "text-success" 
                                  : isCurrent 
                                  ? "text-primary" 
                                  : "text-muted-foreground/50"
                              }`}>
                                {step.name}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="px-5 py-3 bg-muted/30 border-t border-border/50 flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      {gen.word_count > 0 && (
                        <span>{gen.word_count} words</span>
                      )}
                      {gen.estimated_read_time !== "-" && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {gen.estimated_read_time} read
                        </span>
                      )}
                      <span className="text-muted-foreground/50">{formatDate(gen.created_at)}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-medium text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                      View Details
                      <ChevronRight className="h-4 w-4" />
                    </div>
                  </div>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredGenerations.length === 0 && (
        <Card className="p-12 text-center">
          <Sparkles className="h-10 w-10 text-muted-foreground/30 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-1">No generations found</h3>
          <p className="text-muted-foreground mb-6">
            {searchQuery ? "Try a different search term" : "Start by creating your first post"}
          </p>
          <Link to="/app/generate">
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Create Post
            </Button>
          </Link>
        </Card>
      )}
    </div>
  );
}
