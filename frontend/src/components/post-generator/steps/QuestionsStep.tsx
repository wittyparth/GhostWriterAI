import { motion } from "framer-motion";
import { HelpCircle, CheckCircle, AlertCircle, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useGenerationStore, ClarifyingQuestion } from "@/stores/generationStore";

interface QuestionsStepProps {
  onSubmitAnswers?: () => void;
  // Optional props for history view
  questions?: ClarifyingQuestion[];
  answers?: Record<string, string>;
  isHistoryView?: boolean;
}

export function QuestionsStep({ 
  onSubmitAnswers, 
  questions: propQuestions, 
  answers: propAnswers,
  isHistoryView = false 
}: QuestionsStepProps) {
  const store = useGenerationStore();
  
  // Use props if provided (history view), otherwise use store
  const questions = propQuestions ?? store.strategistOutput?.clarifying_questions ?? [];
  const questionAnswers = propAnswers ?? store.questionAnswers;
  const setQuestionAnswer = store.setQuestionAnswer;
  
  if (questions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">No questions available.</p>
      </div>
    );
  }
  
  const requiredQuestions = questions.filter(q => q.required);
  const answeredRequired = requiredQuestions.filter(
    q => questionAnswers[q.question_id]?.trim()
  ).length;
  const totalAnswered = questions.filter(
    q => questionAnswers[q.question_id]?.trim()
  ).length;
  
  const canSubmit = answeredRequired === requiredQuestions.length;
  const progress = (totalAnswered / questions.length) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-3xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium">
          <HelpCircle className="h-4 w-4" />
          {isHistoryView ? "Your Answers" : "Clarifying Questions"}
        </div>
        
        <h1 className="text-2xl md:text-3xl font-semibold">
          {isHistoryView ? "Questions & Answers" : "Help Us Create Better Content"}
        </h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          {isHistoryView 
            ? "These answers were used to personalize your content."
            : "Answer these questions to personalize your content and maximize engagement."
          }
        </p>
      </div>
      
      {/* Progress */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-2 text-sm">
          <span className="text-muted-foreground">
            {totalAnswered} of {questions.length} answered
          </span>
          <span className="font-mono text-muted-foreground">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-1.5" />
      </Card>
      
      {/* Questions */}
      <div className="space-y-4">
        {questions.map((question, index) => {
          const answer = questionAnswers[question.question_id] || "";
          const isAnswered = answer.trim().length > 0;
          
          return (
            <motion.div
              key={question.question_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className={cn(
                "p-5 transition-colors",
                isAnswered && "border-success/30 bg-success/5"
              )}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono text-muted-foreground">
                      Q{index + 1}
                    </span>
                    {question.required ? (
                      <Badge variant="destructive" className="text-xs">Required</Badge>
                    ) : (
                      <Badge variant="secondary" className="text-xs">Optional</Badge>
                    )}
                  </div>
                  
                  {isAnswered && (
                    <CheckCircle className="h-5 w-5 text-success" />
                  )}
                </div>
                
                <h3 className="font-medium mb-2">{question.question}</h3>
                
                <p className="text-sm text-muted-foreground mb-4 bg-muted/50 p-2.5 rounded-md">
                  💡 {question.rationale}
                </p>
                
                {isHistoryView ? (
                  <div className="bg-muted/30 p-3 rounded-md text-sm">
                    {answer || <span className="text-muted-foreground italic">No answer provided</span>}
                  </div>
                ) : (
                  <Textarea
                    value={answer}
                    onChange={(e) => setQuestionAnswer(question.question_id, e.target.value)}
                    placeholder="Type your answer..."
                    className="min-h-[80px] resize-none"
                  />
                )}
              </Card>
            </motion.div>
          );
        })}
      </div>
      
      {/* Submit - only show in generation flow */}
      {!isHistoryView && onSubmitAnswers && (
        <div className="flex flex-col items-center gap-3 pt-2">
          {!canSubmit && (
            <div className="flex items-center gap-2 text-sm text-warning">
              <AlertCircle className="h-4 w-4" />
              Please answer all required questions
            </div>
          )}
          
          <Button
            size="lg"
            onClick={onSubmitAnswers}
            disabled={!canSubmit}
            className="gap-2 px-8"
          >
            Continue to Writing <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </motion.div>
  );
}
