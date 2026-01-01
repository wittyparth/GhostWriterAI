
import { useQuery } from '@tanstack/react-query';
import { getUsage } from '@/services/auth';
import { Zap, AlertCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';

export function CreditDisplay() {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['usage'],
    queryFn: getUsage,
    refetchInterval: 30000, // Refresh every 30s to keep in sync
  });

  if (isLoading) {
    return (
      <div className="p-4 rounded-xl border space-y-3">
        <div className="flex justify-between">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-10" />
        </div>
        <Skeleton className="h-2 w-full" />
      </div>
    );
  }

  if (!usage) return null;

  const percentage = Math.min(100, (usage.posts_used_today / usage.daily_limit) * 100);
  const isLow = usage.credits_remaining <= 1;
  const isZero = usage.credits_remaining === 0;

  let progressColor = "bg-primary";
  if (isZero) progressColor = "bg-destructive";
  else if (isLow) progressColor = "bg-amber-500";

  return (
    <div className="p-4 rounded-xl bg-gradient-to-br from-card to-secondary/30 border border-border/50 space-y-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={cn("p-1.5 rounded-md", isZero ? "bg-destructive/10 text-destructive" : "bg-primary/10 text-primary")}>
            <Zap className="w-4 h-4 fill-current" />
          </div>
          <span className="font-semibold text-sm">Free Credits</span>
        </div>
        <span className={cn("text-sm font-bold font-mono bg-background px-2 py-0.5 rounded border", isZero && "text-destructive border-destructive/30")}>
          {usage.credits_remaining}/{usage.daily_limit}
        </span>
      </div>
      
      <div className="space-y-1.5">
        <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-secondary">
          <div
            className={cn("h-full w-full flex-1 transition-all duration-500 ease-in-out", progressColor)}
            style={{ 
              transform: `translateX(-${100 - percentage}%)`,
              width: '100%' 
            }}
          />
        </div>
        <div className="flex justify-between items-center text-[10px] text-muted-foreground">
          <span>Daily Usage</span>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>Resets midnight</span>
          </div>
        </div>
      </div>

      {isZero && (
        <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/5 p-2 rounded-lg border border-destructive/10">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>You've reached your daily limit. Upgrade for unlimited posts!</span>
        </div>
      )}
    </div>
  );
}
