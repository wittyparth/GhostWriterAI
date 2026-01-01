import { motion } from "framer-motion";
import { LucideIcon, Check, AlertCircle, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { AgentStatus } from "@/stores/generationStore";

interface AgentPageLayoutProps {
  agentName: string;
  agentIcon: LucideIcon;
  agentColor: "validator" | "strategist" | "writer" | "visual" | "optimizer";
  status: AgentStatus;
  progress: number;
  thoughts: string[];
  executionTime?: number;
  children: React.ReactNode;
}

const colorClasses = {
  validator: {
    bg: "bg-agent-validator",
    text: "text-agent-validator",
    border: "border-agent-validator/40",
    bgLight: "bg-agent-validator/10",
  },
  strategist: {
    bg: "bg-agent-strategist",
    text: "text-agent-strategist",
    border: "border-agent-strategist/40",
    bgLight: "bg-agent-strategist/10",
  },
  writer: {
    bg: "bg-agent-writer",
    text: "text-agent-writer",
    border: "border-agent-writer/40",
    bgLight: "bg-agent-writer/10",
  },
  visual: {
    bg: "bg-agent-visual",
    text: "text-agent-visual",
    border: "border-agent-visual/40",
    bgLight: "bg-agent-visual/10",
  },
  optimizer: {
    bg: "bg-agent-optimizer",
    text: "text-agent-optimizer",
    border: "border-agent-optimizer/40",
    bgLight: "bg-agent-optimizer/10",
  },
};

export function AgentPageLayout({
  agentName,
  agentIcon: Icon,
  agentColor,
  status,
  progress,
  thoughts,
  executionTime,
  children,
}: AgentPageLayoutProps) {
  const colors = colorClasses[agentColor];
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="grid lg:grid-cols-[300px_1fr] gap-6"
    >
      {/* Left Panel - Agent Info & Thoughts */}
      <div className="space-y-4">
        {/* Agent Header Card */}
        <Card className={cn("p-5", colors.border)}>
          <div className="flex items-center gap-3 mb-4">
            <div
              className={cn(
                "h-11 w-11 rounded-lg flex items-center justify-center text-white",
                colors.bg
              )}
            >
              <Icon className="h-5 w-5" />
            </div>
            
            <div className="flex-1">
              <h2 className="text-lg font-semibold">{agentName}</h2>
              <div className="flex items-center gap-2 mt-0.5">
                {status === "pending" && (
                  <Badge variant="secondary" className="text-xs">Waiting</Badge>
                )}
                {status === "active" && (
                  <Badge className={cn(colors.bg, "text-white text-xs")}>
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    Processing
                  </Badge>
                )}
                {status === "success" && (
                  <Badge className="bg-success text-success-foreground text-xs">
                    <Check className="h-3 w-3 mr-1" />
                    Complete
                  </Badge>
                )}
                {status === "error" && (
                  <Badge variant="destructive" className="text-xs">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Error
                  </Badge>
                )}
                {status === "skipped" && (
                  <Badge variant="secondary" className="text-xs">Skipped</Badge>
                )}
                
                {executionTime && (
                  <span className="text-xs text-muted-foreground font-mono">
                    {executionTime.toFixed(1)}s
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          {status === "active" && (
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Progress</span>
                <span className="font-mono">{progress}%</span>
              </div>
              <Progress value={progress} className="h-1.5" />
            </div>
          )}
        </Card>
        
        {/* Thoughts Stream */}
        <Card className="p-4">
          <h3 className="text-sm font-medium mb-3 text-muted-foreground">Agent Thoughts</h3>
          
          <div className="space-y-2 max-h-[280px] overflow-y-auto scrollbar-thin">
            {thoughts.length === 0 ? (
              <p className="text-sm text-muted-foreground/60 italic">
                Waiting for agent to start...
              </p>
            ) : (
              thoughts.map((thought, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "text-sm p-2.5 rounded-md bg-muted/50 border-l-2",
                    colors.border
                  )}
                >
                  {thought}
                </motion.div>
              ))
            )}
            
            {status === "active" && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                Thinking...
              </div>
            )}
          </div>
        </Card>
      </div>
      
      {/* Right Panel - Agent Output */}
      <div className="space-y-4">
        {children}
      </div>
    </motion.div>
  );
}
