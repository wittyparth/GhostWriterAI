import { cn } from "@/lib/utils";

interface SectionHeaderProps {
  badge?: string;
  title: string;
  description?: string;
  className?: string;
  align?: "left" | "center";
}

export function SectionHeader({ 
  badge, 
  title, 
  description, 
  className,
  align = "center" 
}: SectionHeaderProps) {
  return (
    <div className={cn(
      "max-w-3xl",
      align === "center" && "mx-auto text-center",
      className
    )}>
      {badge && (
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 text-accent-400 text-sm font-medium mb-4">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
          </span>
          {badge}
        </div>
      )}
      <h2 className="text-heading-1 text-foreground">{title}</h2>
      {description && (
        <p className="mt-4 text-lg text-muted-foreground">{description}</p>
      )}
    </div>
  );
}
