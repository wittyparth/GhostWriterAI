import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface AnimatedCounterProps {
  value: number | string;
  label: string;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function AnimatedCounter({ 
  value, 
  label, 
  prefix = "", 
  suffix = "",
  className 
}: AnimatedCounterProps) {
  return (
    <motion.div 
      className={cn("text-center", className)}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-3xl md:text-4xl font-display font-bold gradient-text">
        {prefix}{value}{suffix}
      </div>
      <div className="text-sm text-muted-foreground mt-1">{label}</div>
    </motion.div>
  );
}
