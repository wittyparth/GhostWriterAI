import { motion } from "framer-motion";
import { Zap, CheckCircle, RefreshCw, Lightbulb, AlertTriangle, BarChart3 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useGenerationStore, OptimizerOutput, AgentExecution } from "@/stores/generationStore";
import { AgentPageLayout } from "../AgentPageLayout";

interface OptimizerStepProps {
  // Optional props for history view
  agentState?: AgentExecution;
  output?: OptimizerOutput;
}

export function OptimizerStep({ agentState: propAgentState, output: propOutput }: OptimizerStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const agentState = propAgentState ?? store.agents.optimizer;
  const optimizerOutput = propOutput ?? store.optimizerOutput;

  return (
    <AgentPageLayout
      agentName="Optimizer"
      agentIcon={Zap}
      agentColor="optimizer"
      status={agentState.status}
      progress={agentState.progress}
      thoughts={agentState.thoughts}
      executionTime={agentState.execution_time_ms ? agentState.execution_time_ms / 1000 : undefined}
    >
      {optimizerOutput ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Decision Banner */}
          <Card className={cn(
            "p-5",
            optimizerOutput.decision === "APPROVE" 
              ? "border-success/30 bg-success/5" 
              : "border-warning/30 bg-warning/5"
          )}>
            <div className="flex items-start gap-3">
              <div className={optimizerOutput.decision === "APPROVE" ? "text-success" : "text-warning"}>
                {optimizerOutput.decision === "APPROVE" 
                  ? <CheckCircle className="h-6 w-6" />
                  : <RefreshCw className="h-6 w-6" />
                }
              </div>
              <div className="flex-1">
                <h3 className={cn(
                  "font-semibold",
                  optimizerOutput.decision === "APPROVE" ? "text-success" : "text-warning"
                )}>
                  {optimizerOutput.decision === "APPROVE" ? "Content Approved" : "Revision Recommended"}
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {optimizerOutput.decision === "APPROVE" 
                    ? "Your post meets quality standards and is ready to publish."
                    : "The optimizer suggests some improvements before publishing."
                  }
                </p>
              </div>
            </div>
          </Card>
          
          {/* Scores */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Quality Score</span>
                <span className="text-xl font-semibold font-mono">
                  {optimizerOutput.quality_score.toFixed(1)}
                </span>
              </div>
              <Progress value={optimizerOutput.quality_score * 10} className="h-1.5" />
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Brand Consistency</span>
                <span className="text-xl font-semibold font-mono">
                  {optimizerOutput.brand_consistency_score.toFixed(1)}
                </span>
              </div>
              <Progress value={optimizerOutput.brand_consistency_score * 10} className="h-1.5" />
            </Card>
          </div>
          
          {/* Predictions */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
              <BarChart3 className="h-4 w-4" /> Predicted Performance
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 rounded-md bg-muted/30">
                <div className="text-lg font-semibold font-mono">
                  {(optimizerOutput.predicted_impressions_min / 1000).toFixed(1)}K
                </div>
                <div className="text-xs text-muted-foreground">Min Views</div>
              </div>
              <div className="text-center p-3 rounded-md bg-primary/10">
                <div className="text-lg font-semibold font-mono text-primary">
                  {(optimizerOutput.predicted_impressions_max / 1000).toFixed(1)}K
                </div>
                <div className="text-xs text-muted-foreground">Max Views</div>
              </div>
              <div className="text-center p-3 rounded-md bg-muted/30">
                <div className="text-lg font-semibold font-mono">
                  {optimizerOutput.predicted_engagement_rate.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground">Engagement</div>
              </div>
            </div>
            
            <div className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <span>Confidence:</span>
              <div className="flex items-center gap-1.5">
                <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${optimizerOutput.confidence}%` }}
                  />
                </div>
                <span className="font-mono">{optimizerOutput.confidence}%</span>
              </div>
            </div>
          </Card>
          
          {/* Formatting Issues */}
          {optimizerOutput.formatting_issues.length > 0 && (
            <Card className="p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-warning" /> Formatting Issues
              </h3>
              <ul className="space-y-1.5">
                {optimizerOutput.formatting_issues.map((issue, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-warning mt-0.5">•</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </Card>
          )}
          
          {/* Suggestions */}
          {optimizerOutput.suggestions.length > 0 && (
            <Card className="p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-primary" /> Suggestions
              </h3>
              <ul className="space-y-1.5">
                {optimizerOutput.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <span className="text-primary mt-0.5">→</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </motion.div>
      ) : (
        <Card className="p-12">
          <div className="flex flex-col items-center justify-center text-center">
            {agentState.status === "active" ? (
              <>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary animate-pulse" />
                </div>
                <h3 className="font-medium">Optimizing Content</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Analyzing quality, predicting performance...
                </p>
              </>
            ) : (
              <>
                <Zap className="h-10 w-10 text-muted-foreground/30 mb-4" />
                <h3 className="font-medium text-muted-foreground">Waiting for Writer</h3>
              </>
            )}
          </div>
        </Card>
      )}
    </AgentPageLayout>
  );
}
