import { motion } from "framer-motion";
import { Check, ChevronLeft, ChevronRight, Search, Target, Pen, Brain, Zap, HelpCircle, FileText, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { GenerationStep, STEP_ORDER, STEP_LABELS, useGenerationStore } from "@/stores/generationStore";

const stepIcons: Record<GenerationStep, React.ElementType> = {
  input: Sparkles,
  validator: Search,
  strategist: Target,
  questions: HelpCircle,
  writer: Pen,
  visual: Brain,
  optimizer: Zap,
  review: FileText,
};

interface StepNavigationProps {
  // Standard props for generation flow
  canGoNext?: boolean;
  onNext?: () => void;
  onPrevious?: () => void;
  nextLabel?: string;
  showNavButtons?: boolean;
  hideVisualStep?: boolean;
  maxCompletedStep?: GenerationStep;
  
  // Override props for history view
  steps?: GenerationStep[];
  currentStep?: GenerationStep;
  completedSteps?: GenerationStep[];
  onStepClick?: (step: GenerationStep) => void;
  stepLabels?: Partial<Record<GenerationStep, string>>;
}

export function StepNavigation({
  canGoNext = true,
  onNext,
  onPrevious,
  nextLabel = "Continue",
  showNavButtons = true,
  hideVisualStep = false,
  maxCompletedStep,
  // History view overrides
  steps: customSteps,
  currentStep: customCurrentStep,
  completedSteps,
  onStepClick: customOnStepClick,
  stepLabels: customStepLabels,
}: StepNavigationProps) {
  const store = useGenerationStore();
  
  // Use custom props if provided (history view), otherwise use store
  const isHistoryView = !!customSteps;
  const currentStep = customCurrentStep ?? store.currentStep;
  const setCurrentStep = customOnStepClick ?? store.setCurrentStep;
  const goToNextStep = onNext ?? store.goToNextStep;
  const goToPreviousStep = onPrevious ?? store.goToPreviousStep;
  const labels = { ...STEP_LABELS, ...customStepLabels };
  
  const visibleSteps = customSteps ?? (hideVisualStep 
    ? STEP_ORDER.filter(s => s !== "visual")
    : STEP_ORDER);
  
  const currentIndex = visibleSteps.indexOf(currentStep);
  const isFirstStep = currentIndex === 0;
  const isLastStep = currentIndex === visibleSteps.length - 1;
  
  // Determine the furthest step reached based on outputs (only for generation flow)
  const getFurthestStep = (): GenerationStep => {
    if (isHistoryView) return visibleSteps[visibleSteps.length - 1];
    
    const { optimizerOutput, writerOutput, strategistOutput, validatorOutput, agents, questionAnswers } = store;
    if (optimizerOutput) return "review";
    if (writerOutput) return "optimizer";
    if (strategistOutput && Object.keys(questionAnswers).length > 0) return "writer";
    if (strategistOutput) return "questions";
    if (validatorOutput) return "strategist";
    if (agents.validator.status !== "pending") return "validator";
    return "input";
  };
  
  const furthestStep = maxCompletedStep || getFurthestStep();
  const furthestIndex = visibleSteps.indexOf(furthestStep);
  
  const getStepStatus = (step: GenerationStep): "complete" | "current" | "upcoming" | "accessible" => {
    const stepIndex = visibleSteps.indexOf(step);
    
    // In history view, all steps are complete except current
    if (isHistoryView) {
      if (stepIndex === currentIndex) return "current";
      return "complete";
    }
    
    if (stepIndex < currentIndex) return "complete";
    if (stepIndex === currentIndex) return "current";
    if (stepIndex <= furthestIndex) return "accessible";
    return "upcoming";
  };
  
  const canNavigateTo = (step: GenerationStep): boolean => {
    if (isHistoryView) return true;
    const stepIndex = visibleSteps.indexOf(step);
    return stepIndex <= furthestIndex;
  };
  
  const handleStepClick = (step: GenerationStep) => {
    if (canNavigateTo(step)) {
      setCurrentStep(step);
    }
  };
  
  const handleNext = () => {
    goToNextStep();
  };
  
  const handlePrevious = () => {
    goToPreviousStep();
  };

  return (
    <div className="space-y-4">
      {/* Step Indicators - Full Width */}
      <div className="w-full">
        <div className="flex items-start justify-between w-full">
          {visibleSteps.map((step, index) => {
            const status = getStepStatus(step);
            const Icon = stepIcons[step];
            const isClickable = canNavigateTo(step);
            
            return (
              <div key={step} className="flex-1 flex flex-col items-center relative">
                {/* Connector line - positioned behind */}
                {index < visibleSteps.length - 1 && (
                  <div 
                    className={cn(
                      "absolute top-4 left-1/2 w-full h-0.5 transition-colors duration-200",
                      status === "complete" ? "bg-success" : "bg-border"
                    )} 
                  />
                )}
                
                {/* Step button */}
                <button
                  onClick={() => handleStepClick(step)}
                  disabled={!isClickable}
                  className={cn(
                    "relative z-10 h-8 w-8 rounded-full flex items-center justify-center transition-all duration-200 border-2",
                    status === "complete" && "bg-success border-success text-success-foreground cursor-pointer hover:opacity-90",
                    status === "current" && "bg-primary border-primary text-primary-foreground",
                    status === "accessible" && "bg-background border-border text-foreground cursor-pointer hover:border-primary",
                    status === "upcoming" && "bg-muted border-border text-muted-foreground/50 cursor-not-allowed"
                  )}
                >
                  {status === "complete" ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Icon className="h-3.5 w-3.5" />
                  )}
                </button>
                
                {/* Step label */}
                <span className={cn(
                  "mt-2 text-xs font-medium text-center px-1 transition-colors",
                  status === "current" && "text-primary",
                  status === "complete" && "text-success",
                  status === "accessible" && "text-foreground",
                  status === "upcoming" && "text-muted-foreground/50"
                )}>
                  {labels[step]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="relative h-1 bg-muted rounded-full overflow-hidden">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${((currentIndex + 1) / visibleSteps.length) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      
      {/* Navigation Buttons - hide in history view since it has its own nav */}
      {showNavButtons && !isHistoryView && (
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={handlePrevious}
            disabled={isFirstStep}
            className="gap-1.5"
          >
            <ChevronLeft className="h-4 w-4" />
            Back
          </Button>
          
          <span className="text-sm text-muted-foreground">
            Step {currentIndex + 1} of {visibleSteps.length}
          </span>
          
          {!isLastStep && (
            <Button
              size="sm"
              onClick={handleNext}
              disabled={!canGoNext}
              className="gap-1.5"
            >
              {nextLabel}
              <ChevronRight className="h-4 w-4" />
            </Button>
          )}
          
          {isLastStep && <div className="w-16" />}
        </div>
      )}
    </div>
  );
}
