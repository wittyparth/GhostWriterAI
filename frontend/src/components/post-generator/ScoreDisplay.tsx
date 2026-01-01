import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";

interface ScoreDisplayProps {
  score: number;
  maxScore?: number;
  label: string;
  animate?: boolean;
  size?: "sm" | "md" | "lg";
  showProgress?: boolean;
}

export function ScoreDisplay({
  score,
  maxScore = 10,
  label,
  animate = true,
  size = "md",
  showProgress = true,
}: ScoreDisplayProps) {
  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);

  useEffect(() => {
    if (!animate) {
      setDisplayScore(score);
      return;
    }

    const duration = 1000;
    const startTime = performance.now();
    const startValue = 0;

    const animateScore = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      setDisplayScore(startValue + (score - startValue) * eased);

      if (progress < 1) {
        requestAnimationFrame(animateScore);
      }
    };

    requestAnimationFrame(animateScore);
  }, [score, animate]);

  const getScoreColor = () => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 90) return "text-agent-validator";
    if (percentage >= 70) return "text-success";
    if (percentage >= 50) return "text-warning";
    return "text-destructive";
  };

  const getProgressColor = () => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 90) return "bg-agent-validator";
    if (percentage >= 70) return "bg-success";
    if (percentage >= 50) return "bg-warning";
    return "bg-destructive";
  };

  const sizeClasses = {
    sm: "text-lg",
    md: "text-2xl",
    lg: "text-4xl",
  };

  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <motion.span
          className={cn("font-mono font-bold", sizeClasses[size], getScoreColor())}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
        >
          {displayScore.toFixed(1)}
          <span className="text-muted-foreground text-sm font-normal">/{maxScore}</span>
        </motion.span>
      </div>
      {showProgress && (
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <motion.div
            className={cn("h-full rounded-full", getProgressColor())}
            initial={{ width: 0 }}
            animate={{ width: `${(score / maxScore) * 100}%` }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
          />
        </div>
      )}
    </div>
  );
}