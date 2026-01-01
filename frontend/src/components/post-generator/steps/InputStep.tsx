import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { useGenerationStore } from "@/stores/generationStore";

const ideaSuggestions = [
  "3 lessons from failing my first startup",
  "Why I quit my corporate job at 30",
  "The morning routine that changed my productivity",
  "What I'd tell my younger self about career growth",
];

const formatOptions = [
  { value: "auto", label: "Auto-detect", description: "Let AI choose the best format" },
  { value: "text", label: "Text Post", description: "Simple text-based post" },
  { value: "carousel", label: "Carousel", description: "Multi-slide visual content" },
];

interface InputStepProps {
  onSubmit: () => void;
}

export function InputStep({ onSubmit }: InputStepProps) {
  const { rawIdea, setRawIdea, preferredFormat, setPreferredFormat } = useGenerationStore();
  
  const canSubmit = rawIdea.length >= 10;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-2xl mx-auto space-y-8"
    >
      {/* Hero Section */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium">
          <Sparkles className="h-4 w-4" />
          AI-Powered Content
        </div>
        
        <h1 className="text-3xl md:text-4xl font-semibold text-foreground">
          What's your idea?
        </h1>
        <p className="text-muted-foreground text-lg max-w-md mx-auto">
          Share your LinkedIn post idea and our AI agents will craft the perfect content.
        </p>
      </div>

      {/* Input Card */}
      <Card className="overflow-hidden">
        <Textarea
          value={rawIdea}
          onChange={(e) => setRawIdea(e.target.value)}
          placeholder="e.g., 3 lessons I learned from failing my first startup after 18 months..."
          className="min-h-[160px] text-base p-5 bg-transparent border-0 resize-none focus-visible:ring-0 placeholder:text-muted-foreground/60"
        />
        <div className="px-5 py-3 bg-muted/30 border-t flex items-center justify-between">
          <span className="text-sm text-muted-foreground font-mono">
            {rawIdea.length} / 5000
          </span>
          {rawIdea.length < 10 && rawIdea.length > 0 && (
            <span className="text-sm text-warning">
              Need at least 10 characters
            </span>
          )}
        </div>
      </Card>

      {/* Quick Starters */}
      <div>
        <p className="text-sm text-muted-foreground mb-3 text-center">Try one of these:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {ideaSuggestions.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setRawIdea(suggestion)}
              className="px-3 py-1.5 rounded-md bg-secondary hover:bg-secondary/80 text-sm text-secondary-foreground transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Format Selection */}
      <Card className="p-5">
        <h3 className="font-medium mb-4 text-foreground">Content Format</h3>
        <RadioGroup
          value={preferredFormat}
          onValueChange={(value: "auto" | "text" | "carousel" | "video") => setPreferredFormat(value)}
          className="grid gap-3"
        >
          {formatOptions.map((option) => (
            <div key={option.value} className="flex items-center space-x-3">
              <RadioGroupItem value={option.value} id={option.value} />
              <Label htmlFor={option.value} className="flex-1 cursor-pointer">
                <span className="font-medium text-foreground">{option.label}</span>
                <span className="text-sm text-muted-foreground ml-2">
                  — {option.description}
                </span>
              </Label>
            </div>
          ))}
        </RadioGroup>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-center">
        <Button
          size="lg"
          onClick={onSubmit}
          disabled={!canSubmit}
          className="gap-2 px-8"
        >
          Generate Post <ArrowRight className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}
