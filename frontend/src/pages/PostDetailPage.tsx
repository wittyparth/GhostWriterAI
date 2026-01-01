import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Trash2, ChevronRight } from "lucide-react";
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

// Mock historical data
const mockHistoricalPost = {
  post_id: "1",
  raw_idea: "3 lessons I learned from failing my first startup after 18 months",
  preferred_format: "text" as const,
  created_at: "2024-01-15T10:30:00Z",
  
  validatorOutput: {
    decision: "APPROVE" as const,
    quality_score: 8.5,
    brand_alignment_score: 8.0,
    reasoning: "Strong personal narrative with valuable lessons.",
    concerns: ["Could benefit from more specific metrics"],
    refinement_suggestions: ["Add specific revenue or user numbers"],
  },
  
  strategistOutput: {
    recommended_format: "text" as const,
    format_reasoning: "Text format works best for personal stories.",
    structure_type: "story_post",
    hook_types: ["personal_story", "contrarian", "data_shock"],
    psychological_triggers: ["curiosity", "relatability"],
    tone: "authentic and vulnerable",
    clarifying_questions: [
      { question_id: "q1", question: "What was the specific amount you lost?", rationale: "Numbers make stories credible", required: true },
      { question_id: "q2", question: "What's the single biggest lesson?", rationale: "Focus creates impact", required: true },
    ],
    similar_posts: [],
  },
  
  questionAnswers: { q1: "$500,000 in total funding", q2: "Validate before you build" },
  
  writerOutput: {
    hooks: [
      { version: 1, text: "I burned through $500K before learning this one lesson.", hook_type: "personal_story", score: 9.2, reasoning: "Strong emotional opening" },
      { version: 2, text: "My startup died after 18 months. Here's why I'm grateful.", hook_type: "contrarian", score: 8.7, reasoning: "Unexpected twist" },
    ],
    body_content: `In 2022, I was convinced we had the next big thing.\n\n18 months and $500K later, I learned the hardest lesson:\n\nWe were solving a problem that didn't exist.\n\n1️⃣ The signs were there from day one\n2️⃣ Burning money doesn't mean you're moving forward\n3️⃣ The best lesson cost the most\n\nToday, I run a profitable business built on one principle:\n\nValidate before you build.`,
    cta: "What's the biggest lesson failure taught you? 👇",
    hashtags: ["startup", "entrepreneurship", "failure", "lessons"],
    formatting_metadata: { word_count: 180, reading_time_seconds: 45, line_count: 28 },
  },
  
  optimizerOutput: {
    decision: "APPROVE" as const,
    quality_score: 8.5,
    brand_consistency_score: 8.0,
    formatting_issues: [],
    suggestions: ["Consider adding a specific metric"],
    predicted_impressions_min: 5000,
    predicted_impressions_max: 15000,
    predicted_engagement_rate: 4.5,
    confidence: 85,
  },
  
  selectedHookIndex: 0,
};

const HISTORY_STEPS: GenerationStep[] = ["validator", "strategist", "questions", "writer", "optimizer", "review"];

export default function PostDetailPage() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<GenerationStep>("validator");
  const [selectedHookIndex, setSelectedHookIndex] = useState(0);

  const completedAgent: AgentExecution = { status: "success", progress: 100, thoughts: [] };
  const currentStepIndex = HISTORY_STEPS.indexOf(currentStep);

  const renderStep = () => {
    switch (currentStep) {
      case "validator":
        return <ValidatorStep agentState={completedAgent} output={mockHistoricalPost.validatorOutput} rawIdea={mockHistoricalPost.raw_idea} />;
      case "strategist":
        return <StrategistStep agentState={completedAgent} output={mockHistoricalPost.strategistOutput} />;
      case "questions":
        return <QuestionsStep questions={mockHistoricalPost.strategistOutput.clarifying_questions} answers={mockHistoricalPost.questionAnswers} isHistoryView />;
      case "writer":
        return <WriterStep agentState={completedAgent} output={mockHistoricalPost.writerOutput} selectedHookIndex={selectedHookIndex} onHookSelect={setSelectedHookIndex} />;
      case "optimizer":
        return <OptimizerStep agentState={completedAgent} output={mockHistoricalPost.optimizerOutput} />;
      case "review":
        return <ReviewStep writerOutput={mockHistoricalPost.writerOutput} optimizerOutput={mockHistoricalPost.optimizerOutput} selectedHookIndex={selectedHookIndex} onStartOver={() => navigate("/app/generate")} />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={() => navigate("/app/posts")} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back to Posts
        </Button>
        <Button variant="destructive" size="sm" onClick={() => { toast.success("Post deleted"); navigate("/app/posts"); }}>
          <Trash2 className="mr-2 h-4 w-4" /> Delete
        </Button>
      </div>

      <Card className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge variant="secondary" className="mb-2">{mockHistoricalPost.preferred_format}</Badge>
            <h1 className="text-xl font-semibold mb-1">{mockHistoricalPost.raw_idea}</h1>
            <p className="text-sm text-muted-foreground">Generated {new Date(mockHistoricalPost.created_at).toLocaleDateString()}</p>
          </div>
          <div className="bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 px-3 py-1.5 rounded-lg font-semibold">
            {mockHistoricalPost.optimizerOutput.quality_score}/10
          </div>
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
