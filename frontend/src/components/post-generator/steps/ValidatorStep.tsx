import { motion } from "framer-motion";
import { Search, CheckCircle, AlertTriangle, XCircle, Lightbulb } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { useGenerationStore, ValidatorOutput, AgentExecution } from "@/stores/generationStore";
import { AgentPageLayout } from "../AgentPageLayout";

interface ValidatorStepProps {
  // Optional props for history view
  agentState?: AgentExecution;
  output?: ValidatorOutput;
  rawIdea?: string;
}

export function ValidatorStep({ agentState: propAgentState, output: propOutput, rawIdea: propRawIdea }: ValidatorStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const agentState = propAgentState ?? store.agents.validator;
  const validatorOutput = propOutput ?? store.validatorOutput;
  const rawIdea = propRawIdea ?? store.rawIdea;
  
  const getDecisionColor = () => {
    if (!validatorOutput) return "text-muted-foreground";
    switch (validatorOutput.decision) {
      case "APPROVE": return "text-success";
      case "REFINE": return "text-warning";
      case "REJECT": return "text-destructive";
    }
  };
  
  const getDecisionIcon = () => {
    if (!validatorOutput) return null;
    switch (validatorOutput.decision) {
      case "APPROVE": return <CheckCircle className="h-6 w-6" />;
      case "REFINE": return <AlertTriangle className="h-6 w-6" />;
      case "REJECT": return <XCircle className="h-6 w-6" />;
    }
  };

  return (
    <AgentPageLayout
      agentName="Validator"
      agentIcon={Search}
      agentColor="validator"
      status={agentState.status}
      progress={agentState.progress}
      thoughts={agentState.thoughts}
      executionTime={agentState.execution_time_ms ? agentState.execution_time_ms / 1000 : undefined}
    >
      {/* Your Idea */}
      <Card className="p-4">
        <h3 className="text-sm font-medium text-muted-foreground mb-2">Your Idea</h3>
        <p className="text-foreground bg-muted/50 p-3 rounded-md text-sm">
          "{rawIdea}"
        </p>
      </Card>
      
      {/* Analysis Results */}
      {validatorOutput ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Decision Banner */}
          <Card className={cn(
            "p-5",
            validatorOutput.decision === "APPROVE" && "border-success/30 bg-success/5",
            validatorOutput.decision === "REFINE" && "border-warning/30 bg-warning/5",
            validatorOutput.decision === "REJECT" && "border-destructive/30 bg-destructive/5"
          )}>
            <div className="flex items-start gap-3">
              <div className={getDecisionColor()}>
                {getDecisionIcon()}
              </div>
              <div className="flex-1">
                <h3 className={cn("text-lg font-semibold", getDecisionColor())}>
                  {validatorOutput.decision === "APPROVE" && "Idea Approved"}
                  {validatorOutput.decision === "REFINE" && "Needs Refinement"}
                  {validatorOutput.decision === "REJECT" && "Idea Rejected"}
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {validatorOutput.reasoning}
                </p>
              </div>
            </div>
          </Card>
          
          {/* Scores */}
          <div className="grid grid-cols-2 gap-4">
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Quality Score</span>
                <span className="text-xl font-semibold font-mono">
                  {validatorOutput.quality_score.toFixed(1)}
                </span>
              </div>
              <Progress value={validatorOutput.quality_score * 10} className="h-1.5" />
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Brand Alignment</span>
                <span className="text-xl font-semibold font-mono">
                  {validatorOutput.brand_alignment_score.toFixed(1)}
                </span>
              </div>
              <Progress value={validatorOutput.brand_alignment_score * 10} className="h-1.5" />
            </Card>
          </div>
          
          {/* Concerns */}
          {validatorOutput.concerns.length > 0 && (
            <Card className="p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-warning" /> Concerns
              </h3>
              <ul className="space-y-1.5">
                {validatorOutput.concerns.map((concern, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-warning mt-0.5">•</span>
                    {concern}
                  </li>
                ))}
              </ul>
            </Card>
          )}
          
          {/* Suggestions */}
          {validatorOutput.refinement_suggestions.length > 0 && (
            <Card className="p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-primary" /> Suggestions
              </h3>
              <ul className="space-y-1.5">
                {validatorOutput.refinement_suggestions.map((suggestion, index) => (
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
                  <Search className="h-6 w-6 text-primary animate-pulse" />
                </div>
                <h3 className="font-medium">Analyzing Your Idea</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Evaluating quality, potential, and brand alignment...
                </p>
              </>
            ) : (
              <>
                <Search className="h-10 w-10 text-muted-foreground/30 mb-4" />
                <h3 className="font-medium text-muted-foreground">Waiting to Analyze</h3>
              </>
            )}
          </div>
        </Card>
      )}
    </AgentPageLayout>
  );
}
