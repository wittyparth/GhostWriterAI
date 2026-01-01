import { motion } from "framer-motion";
import { Pen, Star, Hash, Clock, FileText, Quote } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useGenerationStore, WriterOutput, AgentExecution } from "@/stores/generationStore";
import { AgentPageLayout } from "../AgentPageLayout";

interface WriterStepProps {
  // Optional props for history view
  agentState?: AgentExecution;
  output?: WriterOutput;
  selectedHookIndex?: number;
  onHookSelect?: (index: number) => void;
}

export function WriterStep({ 
  agentState: propAgentState, 
  output: propOutput,
  selectedHookIndex: propSelectedHookIndex,
  onHookSelect: propOnHookSelect
}: WriterStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const agentState = propAgentState ?? store.agents.writer;
  const writerOutput = propOutput ?? store.writerOutput;
  const selectedHookIndex = propSelectedHookIndex ?? store.selectedHookIndex;
  const setSelectedHookIndex = propOnHookSelect ?? store.setSelectedHookIndex;

  return (
    <AgentPageLayout
      agentName="Writer"
      agentIcon={Pen}
      agentColor="writer"
      status={agentState.status}
      progress={agentState.progress}
      thoughts={agentState.thoughts}
      executionTime={agentState.execution_time_ms ? agentState.execution_time_ms / 1000 : undefined}
    >
      {writerOutput ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Hook Variations */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Hook Variations</h3>
            <div className="space-y-2">
              {writerOutput.hooks.map((hook, index) => (
                <div
                  key={hook.version}
                  onClick={() => setSelectedHookIndex(index)}
                  className={cn(
                    "p-3 rounded-md border cursor-pointer transition-colors",
                    selectedHookIndex === index
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className={cn(
                      "h-6 w-6 rounded flex items-center justify-center text-xs font-medium shrink-0",
                      selectedHookIndex === index
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    )}>
                      {hook.version}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium whitespace-pre-line">{hook.text}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="secondary" className="text-xs capitalize">
                          {hook.hook_type.replace(/_/g, " ")}
                        </Badge>
                        <span className="flex items-center gap-1 text-warning text-xs font-mono">
                          <Star className="h-3 w-3 fill-warning" />
                          {hook.score.toFixed(1)}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1.5">{hook.reasoning}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          {/* Body Content */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4" /> Body Content
            </h3>
            <div className="bg-muted/30 p-4 rounded-md whitespace-pre-line text-sm leading-relaxed">
              {writerOutput.body_content}
            </div>
          </Card>
          
          {/* CTA */}
          <Card className="p-4">
            <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <Quote className="h-4 w-4" /> Call to Action
            </h3>
            <div className="bg-primary/10 border border-primary/20 p-3 rounded-md">
              <p className="text-sm font-medium whitespace-pre-line">{writerOutput.cta}</p>
            </div>
          </Card>
          
          {/* Hashtags & Metadata */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                <Hash className="h-4 w-4" /> Hashtags
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {writerOutput.hashtags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            </Card>
            
            <Card className="p-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                <Clock className="h-4 w-4" /> Metrics
              </h3>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div className="text-center">
                  <div className="font-mono font-medium">{writerOutput.formatting_metadata.word_count}</div>
                  <div className="text-xs text-muted-foreground">Words</div>
                </div>
                <div className="text-center">
                  <div className="font-mono font-medium">{writerOutput.formatting_metadata.line_count}</div>
                  <div className="text-xs text-muted-foreground">Lines</div>
                </div>
                <div className="text-center">
                  <div className="font-mono font-medium">{writerOutput.formatting_metadata.reading_time_seconds}s</div>
                  <div className="text-xs text-muted-foreground">Read</div>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      ) : (
        <Card className="p-12">
          <div className="flex flex-col items-center justify-center text-center">
            {agentState.status === "active" ? (
              <>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Pen className="h-6 w-6 text-primary animate-pulse" />
                </div>
                <h3 className="font-medium">Crafting Your Content</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Generating hooks, body content, and call-to-action...
                </p>
              </>
            ) : (
              <>
                <Pen className="h-10 w-10 text-muted-foreground/30 mb-4" />
                <h3 className="font-medium text-muted-foreground">Waiting for Questions</h3>
              </>
            )}
          </div>
        </Card>
      )}
    </AgentPageLayout>
  );
}
