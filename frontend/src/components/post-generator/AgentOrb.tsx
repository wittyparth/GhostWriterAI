import { motion } from "framer-motion";
import { Check, AlertCircle, Loader2, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { AgentStatus } from "./types";

interface AgentOrbProps {
  icon: LucideIcon;
  color: "validator" | "strategist" | "writer" | "visual" | "optimizer";
  status: AgentStatus;
  size?: "sm" | "md" | "lg";
  showScore?: boolean;
  score?: number;
  name?: string;
}

const sizeClasses = {
  sm: "h-10 w-10",
  md: "h-14 w-14",
  lg: "h-20 w-20",
};

const iconSizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
};

const colorClasses = {
  validator: {
    bg: "bg-agent-validator",
    text: "text-agent-validator",
    shadow: "shadow-agent-validator",
    ring: "ring-agent-validator",
  },
  strategist: {
    bg: "bg-agent-strategist",
    text: "text-agent-strategist",
    shadow: "shadow-agent-strategist",
    ring: "ring-agent-strategist",
  },
  writer: {
    bg: "bg-agent-writer",
    text: "text-agent-writer",
    shadow: "shadow-agent-writer",
    ring: "ring-agent-writer",
  },
  visual: {
    bg: "bg-agent-visual",
    text: "text-agent-visual",
    shadow: "shadow-agent-visual",
    ring: "ring-agent-visual",
  },
  optimizer: {
    bg: "bg-agent-optimizer",
    text: "text-agent-optimizer",
    shadow: "shadow-agent-optimizer",
    ring: "ring-agent-optimizer",
  },
};

export function AgentOrb({
  icon: Icon,
  color,
  status,
  size = "md",
  showScore = false,
  score,
  name,
}: AgentOrbProps) {
  const colors = colorClasses[color];

  const getStatusStyles = () => {
    switch (status) {
      case "idle":
        return "bg-muted text-muted-foreground";
      case "active":
        return cn(colors.bg, "text-white", colors.shadow);
      case "complete":
        return cn(colors.bg, "text-white ring-2 ring-offset-2 ring-offset-background", colors.ring);
      case "error":
        return "bg-destructive text-destructive-foreground ring-2 ring-destructive ring-offset-2 ring-offset-background";
      case "skipped":
        return "bg-muted/50 text-muted-foreground/50";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const renderIcon = () => {
    if (status === "complete") {
      return <Check className={iconSizeClasses[size]} />;
    }
    if (status === "error") {
      return <AlertCircle className={iconSizeClasses[size]} />;
    }
    if (status === "active") {
      return (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Icon className={iconSizeClasses[size]} />
        </motion.div>
      );
    }
    return <Icon className={iconSizeClasses[size]} />;
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <motion.div
        className={cn(
          "rounded-full flex items-center justify-center transition-all duration-300",
          sizeClasses[size],
          getStatusStyles(),
          status === "active" && "animate-agent-pulse"
        )}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        whileHover={{ scale: 1.05 }}
      >
        {renderIcon()}
      </motion.div>
      {name && (
        <span className={cn(
          "text-xs font-medium",
          status === "active" ? colors.text : "text-muted-foreground"
        )}>
          {name}
        </span>
      )}
      {showScore && score !== undefined && status === "complete" && (
        <motion.span
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn("text-sm font-mono font-semibold", colors.text)}
        >
          {score.toFixed(1)}
        </motion.span>
      )}
    </div>
  );
}