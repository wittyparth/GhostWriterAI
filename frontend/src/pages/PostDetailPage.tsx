import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, Trash2, ChevronRight, AlertCircle, RefreshCcw } from "lucide-react";
import { toast } from "sonner";
import { StepNavigation } from "@/components/post-generator/StepNavigation";
import {
  ValidatorStep,
  StrategistStep,
  QuestionsStep,
  WriterStep,
  OptimizerStep,
  ReviewStep,
} from "@/components/post-generator/steps";
import type { GenerationStep, AgentExecution } from "@/stores/generationStore";
import { getHistoryDetail, getHistoryByPostId, updateSelectedHook } from "@/services/api";
import { deletePost } from "@/services/posts";

const HISTORY_STEPS: GenerationStep[] = ["validator", "strategist", "questions", "writer", "optimizer", "review"];

export default function PostDetailPage() {
  const { postId, generationId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState<GenerationStep>("validator");
  const [selectedHookIndex, setSelectedHookIndex] = useState(0);

  // Determine which ID to use - could be from /posts/:postId or /generations/:generationId
  const historyId = generationId || postId;

  // Fetch history detail from API
  const { data: history, isLoading, error, refetch } = useQuery({
    queryKey: ['historyDetail', historyId],
    queryFn: async () => {
      if (generationId) {
        // Direct history ID
        return getHistoryDetail(generationId);
      } else if (postId) {
        // Try to get history by post ID
        return getHistoryByPostId(postId);
      }
      throw new Error("No ID provided");
    },
    enabled: !!historyId,
  });

  // Update selected hook mutation
  const updateHookMutation = useMutation({
    mutationFn: (hookIndex: number) => updateSelectedHook(history!.history_id, hookIndex),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['historyDetail', historyId] });
    },
  });

  // Delete post mutation
  const deleteMutation = useMutation({
    mutationFn: () => deletePost(history?.post_id || postId || ""),
    onSuccess: () => {
      toast.success("Post deleted");
      navigate("/app/posts");
    },
    onError: () => {
      toast.error("Failed to delete post");
    },
  });

  const handleHookSelect = (index: number) => {
    setSelectedHookIndex(index);
    if (history) {
      updateHookMutation.mutate(index);
    }
  };

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete this post?")) {
      deleteMutation.mutate();
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-9 w-32" />
          <Skeleton className="h-9 w-24" />
        </div>
        <Card className="p-5">
          <Skeleton className="h-6 w-20 mb-2" />
          <Skeleton className="h-8 w-3/4 mb-2" />
          <Skeleton className="h-4 w-48" />
        </Card>
        <Skeleton className="h-16 w-full" />
        <Card className="p-6">
          <Skeleton className="h-64 w-full" />
        </Card>
      </div>
    );
  }

  // Error state
  if (error || !history) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" onClick={() => navigate("/app/posts")} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back to Posts
        </Button>
        <Card className="p-8 text-center">
          <AlertCircle className="h-10 w-10 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Failed to load post details</h3>
          <p className="text-muted-foreground mb-4">
            {(error as Error)?.message || "Post not found or you don't have access"}
          </p>
          <div className="flex gap-3 justify-center">
            <Button variant="outline" onClick={() => refetch()}>
              <RefreshCcw className="mr-2 h-4 w-4" /> Try Again
            </Button>
            <Button onClick={() => navigate("/app/posts")}>
              Back to Posts
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // Transform API data to component format
  const validatorOutput = {
    decision: history.validator_output?.decision || "APPROVE",
    quality_score: history.validator_output?.quality_score || 0,
    brand_alignment_score: history.validator_output?.brand_alignment_score || 0,
    reasoning: history.validator_output?.reasoning || "",
    concerns: history.validator_output?.concerns || [],
    refinement_suggestions: history.validator_output?.refinement_suggestions || [],
  };

  const strategistOutput = {
    recommended_format: history.strategist_output?.recommended_format || "text",
    format_reasoning: history.strategist_output?.format_reasoning || "",
    structure_type: history.strategist_output?.structure_type || "",
    hook_types: history.strategist_output?.hook_types || [],
    psychological_triggers: history.strategist_output?.psychological_triggers || [],
    tone: history.strategist_output?.tone || "",
    clarifying_questions: history.clarifying_questions || [],
    similar_posts: history.strategist_output?.similar_posts || [],
  };

  const writerOutput = {
    hooks: history.writer_output?.hooks || [],
    body_content: history.writer_output?.body_content || history.final_post?.body || "",
    cta: history.writer_output?.cta || history.final_post?.cta || "",
    hashtags: history.writer_output?.hashtags || history.final_post?.hashtags || [],
    formatting_metadata: history.writer_output?.formatting_metadata || {},
  };

  const optimizerOutput = {
    decision: history.optimizer_output?.decision || "APPROVE",
    quality_score: history.optimizer_output?.quality_score || 0,
    brand_consistency_score: history.optimizer_output?.brand_consistency_score || 0,
    formatting_issues: history.optimizer_output?.formatting_issues || [],
    suggestions: history.optimizer_output?.suggestions || [],
    predicted_impressions_min: history.optimizer_output?.predicted_impressions_min || 0,
    predicted_impressions_max: history.optimizer_output?.predicted_impressions_max || 0,
    predicted_engagement_rate: history.optimizer_output?.predicted_engagement_rate || 0,
    confidence: history.optimizer_output?.confidence || 0,
  };

  const completedAgent: AgentExecution = { status: "success", progress: 100, thoughts: [] };
  const currentStepIndex = HISTORY_STEPS.indexOf(currentStep);

  const renderStep = () => {
    switch (currentStep) {
      case "validator":
        return <ValidatorStep agentState={completedAgent} output={validatorOutput} rawIdea={history.raw_idea} />;
      case "strategist":
        return <StrategistStep agentState={completedAgent} output={strategistOutput} />;
      case "questions":
        return <QuestionsStep questions={history.clarifying_questions || []} answers={history.user_answers || {}} isHistoryView />;
      case "writer":
        return <WriterStep agentState={completedAgent} output={writerOutput} selectedHookIndex={history.selected_hook_index || selectedHookIndex} onHookSelect={handleHookSelect} />;
      case "optimizer":
        return <OptimizerStep agentState={completedAgent} output={optimizerOutput} />;
      case "review":
        return <ReviewStep writerOutput={writerOutput} optimizerOutput={optimizerOutput} selectedHookIndex={history.selected_hook_index || selectedHookIndex} onStartOver={() => navigate("/app/generate")} />;
      default:
        return null;
    }
  };

  const formattedDate = history.started_at ? new Date(history.started_at).toLocaleDateString() : "Unknown";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back
        </Button>
        <Button 
          variant="destructive" 
          size="sm" 
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
        >
          <Trash2 className="mr-2 h-4 w-4" /> Delete
        </Button>
      </div>

      <Card className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">{history.preferred_format || history.final_post?.format || "text"}</Badge>
              <Badge variant={history.status === "completed" ? "success" : history.status === "failed" ? "failed" : "pending"}>
                {history.status}
              </Badge>
            </div>
            <h1 className="text-xl font-semibold mb-1">{history.raw_idea}</h1>
            <p className="text-sm text-muted-foreground">Generated {formattedDate}</p>
          </div>
          {optimizerOutput.quality_score > 0 && (
            <div className="bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 px-3 py-1.5 rounded-lg font-semibold">
              {optimizerOutput.quality_score}/10
            </div>
          )}
        </div>
      </Card>

      <StepNavigation steps={HISTORY_STEPS} currentStep={currentStep} onStepClick={setCurrentStep} showNavButtons={false} />

      <AnimatePresence mode="wait">
        <motion.div key={currentStep} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} transition={{ duration: 0.2 }}>
          {renderStep()}
        </motion.div>
      </AnimatePresence>

      <div className="flex items-center justify-between pt-4 border-t">
        <Button variant="outline" onClick={() => setCurrentStep(HISTORY_STEPS[currentStepIndex - 1])} disabled={currentStepIndex === 0}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Previous
        </Button>
        <span className="text-sm text-muted-foreground">{currentStepIndex + 1} of {HISTORY_STEPS.length}</span>
        <Button onClick={() => setCurrentStep(HISTORY_STEPS[currentStepIndex + 1])} disabled={currentStepIndex === HISTORY_STEPS.length - 1}>
          Next <ChevronRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
