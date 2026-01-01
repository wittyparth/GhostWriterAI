import { cn } from "@/lib/utils";
import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  showText?: boolean;
}

export function Logo({ className, size = "md", showText = true }: LogoProps) {
  const sizes = {
    sm: { icon: "h-6 w-6", text: "text-lg" },
    md: { icon: "h-8 w-8", text: "text-xl" },
    lg: { icon: "h-10 w-10", text: "text-2xl" },
  };

  return (
    <motion.div 
      className={cn("flex items-center gap-2", className)}
      whileHover={{ scale: 1.02 }}
    >
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent rounded-lg blur-lg opacity-50" />
        <div className={cn(
          "relative flex items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent",
          sizes[size].icon
        )}>
          <Sparkles className="h-1/2 w-1/2 text-primary-foreground" />
        </div>
      </div>
      {showText && (
        <span className={cn("font-display font-bold text-foreground", sizes[size].text)}>
          PostAI
        </span>
      )}
    </motion.div>
  );
}
