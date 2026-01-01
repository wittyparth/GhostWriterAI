import { motion } from "framer-motion";
import { Target, FileText, ImageIcon, Video, Brain, Sparkles, MessageSquare } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useGenerationStore, StrategistOutput, AgentExecution } from "@/stores/generationStore";
import { AgentPageLayout } from "../AgentPageLayout";

const formatIcons = {
  text: FileText,
  carousel: ImageIcon,
  video: Video,
};

interface StrategistStepProps {
  // Optional props for history view
  agentState?: AgentExecution;
  output?: StrategistOutput;
}

export function StrategistStep({ agentState: propAgentState, output: propOutput }: StrategistStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const agentState = propAgentState ?? store.agents.strategist;
  const strategistOutput = propOutput ?? store.strategistOutput;
  
  const FormatIcon = strategistOutput 
    ? formatIcons[strategistOutput.recommended_format] 
    : FileText;

  return (
    <AgentPageLayout
      agentName="Strategist"
      agentIcon={Target}
      agentColor="strategist"
      status={agentState.status}
      progress={agentState.progress}
      thoughts={agentState.thoughts}
      executionTime={agentState.execution_time_ms ? agentState.execution_time_ms / 1000 : undefined}
    >
      {strategistOutput ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Format Recommendation */}
          <Card className="p-5 border-primary/30 bg-primary/5">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center text-primary-foreground">
                <FormatIcon className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold capitalize">
                  {strategistOutput.recommended_format} Post Recommended
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {strategistOutput.format_reasoning}
                </p>
              </div>
            </div>
          </Card>
          
          {/* Strategy Details Grid */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                <FileText className="h-4 w-4" /> Structure
              </h3>
              <p className="font-medium capitalize">
                {strategistOutput.structure_type.replace(/_/g, " ")}
              </p>
            </Card>
            
            <Card className="p-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-2">
                <MessageSquare className="h-4 w-4" /> Tone
              </h3>
              <p className="font-medium capitalize">
                {strategistOutput.tone}
              </p>
            </Card>
          </div>
          
          {/* Hook Types */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4" /> Recommended Hook Types
            </h3>
            <div className="flex flex-wrap gap-2">
              {strategistOutput.hook_types.map((hookType) => (
                <Badge 
                  key={hookType}
                  variant="secondary" 
                  className="capitalize"
                >
                  {hookType.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
          </Card>
          
          {/* Psychological Triggers */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <Brain className="h-4 w-4" /> Psychological Triggers
            </h3>
            <div className="flex flex-wrap gap-2">
              {strategistOutput.psychological_triggers.map((trigger) => (
                <Badge 
                  key={trigger}
                  variant="outline"
                  className="capitalize"
                >
                  {trigger.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
          </Card>
          
          {/* Questions Preview */}
          {strategistOutput.clarifying_questions.length > 0 && (
            <Card className="p-4 border-dashed">
              <h3 className="font-medium mb-2">
                {strategistOutput.clarifying_questions.length} Questions Generated
              </h3>
              <p className="text-sm text-muted-foreground">
                Answer these in the next step to help create better content.
              </p>
            </Card>
          )}
        </motion.div>
      ) : (
        <Card className="p-12">
          <div className="flex flex-col items-center justify-center text-center">
            {agentState.status === "active" ? (
              <>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Target className="h-6 w-6 text-primary animate-pulse" />
                </div>
                <h3 className="font-medium">Planning Content Strategy</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Analyzing format, structure, and psychological triggers...
                </p>
              </>
            ) : (
              <>
                <Target className="h-10 w-10 text-muted-foreground/30 mb-4" />
                <h3 className="font-medium text-muted-foreground">Waiting for Validator</h3>
              </>
            )}
          </div>
        </Card>
      )}
    </AgentPageLayout>
  );
}
