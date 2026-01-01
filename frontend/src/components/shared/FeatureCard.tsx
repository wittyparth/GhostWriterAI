import { cn } from "@/lib/utils";
import { motion, HTMLMotionProps } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface FeatureCardProps extends Omit<HTMLMotionProps<"div">, "children"> {
  icon: LucideIcon;
  title: string;
  description: string;
  gradient?: boolean;
}

export function FeatureCard({ 
  icon: Icon, 
  title, 
  description, 
  gradient = false,
  className,
  ...props 
}: FeatureCardProps) {
  return (
    <motion.div
      className={cn(
        "group relative p-6 rounded-2xl glass overflow-hidden",
        "hover:shadow-glow-md transition-all duration-500",
        gradient && "gradient-border",
        className
      )}
      whileHover={{ y: -5, scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
      {...props}
    >
      {/* Background glow on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      <div className="relative z-10">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-4 shadow-glow-sm">
          <Icon className="h-6 w-6 text-primary-foreground" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
        <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>
      </div>
    </motion.div>
  );
}
