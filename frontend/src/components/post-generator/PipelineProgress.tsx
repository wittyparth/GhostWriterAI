import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Agent, AgentState } from "./types";

interface PipelineProgressProps {
  agents: Agent[];
  agentStates: Record<string, AgentState>;
}

const colorClasses = {
  validator: "bg-agent-validator",
  strategist: "bg-agent-strategist",
  writer: "bg-agent-writer",
  visual: "bg-agent-visual",
  optimizer: "bg-agent-optimizer",
};

export function PipelineProgress({ agents, agentStates }: PipelineProgressProps) {
  return (
    <div className="w-full">
      {/* Horizontal stepper */}
      <div className="relative flex items-center justify-between">
        {/* Connecting line */}
        <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-1 bg-border mx-10" />
        
        {/* Progress line */}
        <motion.div
          className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-primary mx-10"
          initial={{ width: "0%" }}
          animate={{
            width: `${Math.max(
              0,
              (agents.findIndex((a) => agentStates[a.id]?.status === "active") / (agents.length - 1)) * 100
            )}%`,
          }}
          transition={{ duration: 0.5 }}
        />

        {agents.map((agent, index) => {
          const state = agentStates[agent.id];
          const isActive = state?.status === "active";
          const isComplete = state?.status === "complete";
          const isSkipped = state?.status === "skipped";
          const isPending = state?.status === "idle" || !state;

          return (
            <div key={agent.id} className="relative z-10 flex flex-col items-center">
              <motion.div
                whileHover={{ scale: 1.1 }}
                className={cn(
                  "h-10 w-10 rounded-full flex items-center justify-center border-2 transition-all bg-background",
                  isComplete && cn("border-0", colorClasses[agent.color]),
                  isActive && cn("border-0", colorClasses[agent.color], "animate-node-pulse"),
                  isPending && "border-muted-foreground/30",
                  isSkipped && "border-dashed border-muted-foreground/30 opacity-50"
                )}
              >
                {isComplete && <Check className="h-5 w-5 text-white" />}
                {isActive && <Loader2 className="h-5 w-5 text-white animate-spin" />}
                {(isPending || isSkipped) && (
                  <span className="text-sm font-medium text-muted-foreground">{index + 1}</span>
                )}
              </motion.div>
              <span className={cn(
                "mt-2 text-xs font-medium text-center max-w-[80px] truncate",
                isActive && "text-foreground",
                isComplete && "text-foreground",
                (isPending || isSkipped) && "text-muted-foreground"
              )}>
                {agent.name}
              </span>
              {isActive && (
                <span className="text-[10px] text-muted-foreground mt-0.5">
                  {state?.progress || 0}%
                </span>
              )}
              {isComplete && state?.duration && (
                <span className="text-[10px] text-success mt-0.5">
                  ✓ {state.duration.toFixed(1)}s
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}