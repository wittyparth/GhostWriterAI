import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";

interface ThoughtBubbleProps {
  thought: string;
  color: "validator" | "strategist" | "writer" | "visual" | "optimizer";
  isLatest?: boolean;
  showTyping?: boolean;
  timestamp?: Date;
}

const borderColorClasses = {
  validator: "border-l-agent-validator",
  strategist: "border-l-agent-strategist",
  writer: "border-l-agent-writer",
  visual: "border-l-agent-visual",
  optimizer: "border-l-agent-optimizer",
};

const bgColorClasses = {
  validator: "bg-agent-validator/5",
  strategist: "bg-agent-strategist/5",
  writer: "bg-agent-writer/5",
  visual: "bg-agent-visual/5",
  optimizer: "bg-agent-optimizer/5",
};

export function ThoughtBubble({
  thought,
  color,
  isLatest = false,
  showTyping = false,
  timestamp,
}: ThoughtBubbleProps) {
  const [displayText, setDisplayText] = useState(showTyping ? "" : thought);
  const [isTyping, setIsTyping] = useState(showTyping);

  useEffect(() => {
    if (!showTyping) {
      setDisplayText(thought);
      return;
    }

    setDisplayText("");
    setIsTyping(true);
    let index = 0;

    const interval = setInterval(() => {
      if (index < thought.length) {
        setDisplayText(thought.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [thought, showTyping]);

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: isLatest ? 1 : 0.7, x: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "pl-4 py-3 pr-4 rounded-lg font-mono text-sm border-l-[3px]",
        borderColorClasses[color],
        bgColorClasses[color],
        isLatest && "shadow-sm"
      )}
    >
      <div className="flex items-start gap-2">
        <span className="text-muted-foreground/60 shrink-0">💭</span>
        <div className="flex-1 min-w-0">
          <p className={cn(
            "text-foreground/90 break-words",
            isLatest && "text-foreground"
          )}>
            "{displayText}
            {isTyping && (
              <span className="inline-block w-0.5 h-4 bg-foreground ml-0.5 animate-typing-cursor" />
            )}
            {!isTyping && '"'}
          </p>
        </div>
      </div>
      {timestamp && (
        <div className="text-right mt-2">
          <span className="text-[10px] text-muted-foreground/50 font-mono">
            {timestamp.toLocaleTimeString()}
          </span>
        </div>
      )}
    </motion.div>
  );
}