import { motion, AnimatePresence } from "framer-motion";
import { Check, ChevronDown, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { Agent, AgentState } from "./types";
import { AgentOrb } from "./AgentOrb";
import { ThoughtStream } from "./ThoughtStream";
import { ScoreDisplay } from "./ScoreDisplay";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface AgentCardProps {
  agent: Agent;
  state: AgentState;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

const colorClasses = {
  validator: {
    border: "border-agent-validator/50",
    shadow: "shadow-agent-validator",
    text: "text-agent-validator",
  },
  strategist: {
    border: "border-agent-strategist/50",
    shadow: "shadow-agent-strategist",
    text: "text-agent-strategist",
  },
  writer: {
    border: "border-agent-writer/50",
    shadow: "shadow-agent-writer",
    text: "text-agent-writer",
  },
  visual: {
    border: "border-agent-visual/50",
    shadow: "shadow-agent-visual",
    text: "text-agent-visual",
  },
  optimizer: {
    border: "border-agent-optimizer/50",
    shadow: "shadow-agent-optimizer",
    text: "text-agent-optimizer",
  },
};

export function AgentCard({
  agent,
  state,
  isExpanded = false,
  onToggleExpand,
}: AgentCardProps) {
  const colors = colorClasses[agent.color];
  const isActive = state.status === "active";
  const isComplete = state.status === "complete";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "rounded-xl border bg-card/80 backdrop-blur-sm transition-all duration-300 overflow-hidden",
        isActive && cn("border-2", colors.border, "shadow-lg", colors.shadow),
        isComplete && "border-border",
        state.status === "idle" && "border-border/50 opacity-60",
        state.status === "skipped" && "border-dashed border-muted opacity-40"
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "p-4 flex items-center gap-4 cursor-pointer",
          onToggleExpand && "hover:bg-muted/30"
        )}
        onClick={onToggleExpand}
      >
        <AgentOrb
          icon={agent.icon}
          color={agent.color}
          status={state.status}
          size="md"
        />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg">{agent.name}</h3>
            {state.status === "active" && (
              <Badge variant="outline" className={cn("animate-pulse", colors.text)}>
                Processing
              </Badge>
            )}
            {state.status === "complete" && (
              <Badge variant="outline" className="text-success border-success/50">
                <Check className="h-3 w-3 mr-1" />
                Done
              </Badge>
            )}
            {state.status === "skipped" && (
              <Badge variant="outline" className="text-muted-foreground">
                Skipped
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground truncate">
            {agent.description}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {state.duration && (
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              {state.duration.toFixed(1)}s
            </div>
          )}
          {onToggleExpand && (
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            </motion.div>
          )}
        </div>
      </div>

      {/* Progress bar for active agent */}
      {isActive && (
        <div className="px-4 pb-2">
          <Progress value={state.progress} className="h-1.5" />
          <p className="text-xs text-muted-foreground mt-1 text-right">
            {state.progress}% complete
          </p>
        </div>
      )}

      {/* Expandable content */}
      <AnimatePresence>
        {(isExpanded || isActive) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4 border-t border-border/50 pt-4">
              {/* Thought Stream */}
              {state.thoughts.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-3">
                    💭 Agent Thoughts
                  </h4>
                  <ThoughtStream
                    thoughts={state.thoughts}
                    color={agent.color}
                  />
                </div>
              )}

              {/* Metrics Row */}
              {isComplete && state.score !== undefined && (
                <div className="grid grid-cols-2 gap-4">
                  <ScoreDisplay
                    score={state.score}
                    label="Quality Score"
                    size="sm"
                  />
                  {state.decision && (
                    <div className="flex flex-col justify-center">
                      <span className="text-sm text-muted-foreground">Decision</span>
                      <span className={cn(
                        "font-semibold",
                        state.decision.includes("APPROVED") ? "text-success" : "text-warning"
                      )}>
                        {state.decision}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}