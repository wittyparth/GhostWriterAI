import { AnimatePresence } from "framer-motion";
import { useGenerationStore } from "@/stores/generationStore";
import { useGeneration } from "@/hooks/useGeneration";
import { StepNavigation, InputStep, ValidatorStep, StrategistStep, QuestionsStep, WriterStep, OptimizerStep, ReviewStep } from "@/components/post-generator";
import { useToast } from "@/hooks/use-toast";
import { useEffect } from "react";

export default function PostGeneratorPage() {
  const store = useGenerationStore();
  const { toast } = useToast();
  const { 
    currentStep, 
    error,
    isGenerating,
    strategistOutput,
    startGeneration,
    submitAnswers: submitAnswersApi,
    startOver 
  } = useGeneration();

  // Show error toast when error occurs
  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  const handleStartGeneration = () => {
    startGeneration();
  };

  const handleSubmitAnswers = () => {
    submitAnswersApi();
  };

  const handleStartOver = () => {
    startOver();
  };

  const hideVisual = !strategistOutput || strategistOutput.recommended_format !== "carousel";

  return (
    <div className="min-h-[calc(100vh-8rem)] space-y-6">
      <StepNavigation 
        hideVisualStep={hideVisual}
        showNavButtons={currentStep !== "input" && currentStep !== "questions" && currentStep !== "review" && !isGenerating}
        canGoNext={false}
      />

      <AnimatePresence mode="wait">
        {currentStep === "input" && <InputStep key="input" onSubmit={handleStartGeneration} />}
        {currentStep === "validator" && <ValidatorStep key="validator" />}
        {currentStep === "strategist" && <StrategistStep key="strategist" />}
        {currentStep === "questions" && <QuestionsStep key="questions" onSubmitAnswers={handleSubmitAnswers} />}
        {currentStep === "writer" && <WriterStep key="writer" />}
        {currentStep === "optimizer" && <OptimizerStep key="optimizer" />}
        {currentStep === "review" && <ReviewStep key="review" onStartOver={handleStartOver} />}
      </AnimatePresence>
    </div>
  );
}

