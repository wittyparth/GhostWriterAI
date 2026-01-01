import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Agent, AgentState } from "./types";

interface ExecutionTimelineProps {
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

export function ExecutionTimeline({ agents, agentStates }: ExecutionTimelineProps) {
  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-5 top-6 bottom-6 w-0.5 bg-border" />

      <div className="space-y-1">
        {agents.map((agent, index) => {
          const state = agentStates[agent.id];
          const isActive = state?.status === "active";
          const isComplete = state?.status === "complete";
          const isSkipped = state?.status === "skipped";
          const isPending = state?.status === "idle" || !state;

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "relative flex items-start gap-4 p-3 rounded-lg transition-all",
                isActive && "bg-muted/50"
              )}
            >
              {/* Node */}
              <div className="relative z-10">
                <motion.div
                  className={cn(
                    "h-10 w-10 rounded-full border-2 flex items-center justify-center transition-all",
                    isComplete && cn("border-0", colorClasses[agent.color]),
                    isActive && cn("border-0", colorClasses[agent.color], "animate-node-pulse"),
                    isPending && "border-muted-foreground/30 bg-background",
                    isSkipped && "border-dashed border-muted-foreground/30 bg-background/50"
                  )}
                >
                  {isComplete && <Check className="h-5 w-5 text-white" />}
                  {isActive && (
                    <Loader2 className="h-5 w-5 text-white animate-spin" />
                  )}
                  {(isPending || isSkipped) && (
                    <agent.icon className="h-5 w-5 text-muted-foreground/50" />
                  )}
                </motion.div>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pt-2">
                <div className="flex items-center gap-2">
                  <h4 className={cn(
                    "font-medium",
                    isActive && "text-foreground",
                    isComplete && "text-foreground",
                    (isPending || isSkipped) && "text-muted-foreground"
                  )}>
                    {agent.name}
                  </h4>
                </div>

                {isComplete && state?.duration && (
                  <p className="text-sm text-muted-foreground flex items-center gap-2">
                    <Check className="h-3 w-3 text-success" />
                    {state.duration.toFixed(1)}s
                    {state.score && (
                      <span className="text-foreground font-mono">
                        {state.score.toFixed(1)}/10
                      </span>
                    )}
                  </p>
                )}

                {isActive && (
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground flex items-center gap-2">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Processing...
                    </p>
                    <div className="h-1 bg-muted rounded-full overflow-hidden max-w-[120px]">
                      <motion.div
                        className={cn("h-full", colorClasses[agent.color])}
                        initial={{ width: 0 }}
                        animate={{ width: `${state?.progress || 0}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </div>
                )}

                {isPending && (
                  <p className="text-sm text-muted-foreground/60">Waiting</p>
                )}

                {isSkipped && (
                  <p className="text-sm text-muted-foreground/60 line-through">
                    Skipped
                  </p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}