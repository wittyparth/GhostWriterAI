import { create } from "zustand";

// === Agent Output Types (from DATA_FLOW_SPECIFICATION) ===

export interface ValidatorOutput {
  decision: "APPROVE" | "REFINE" | "REJECT";
  quality_score: number;
  brand_alignment_score: number;
  reasoning: string;
  concerns: string[];
  refinement_suggestions: string[];
}

export interface ClarifyingQuestion {
  question_id: string;
  question: string;
  rationale: string;
  required: boolean;
}

export interface StrategistOutput {
  recommended_format: "text" | "carousel" | "video";
  format_reasoning: string;
  structure_type: string;
  hook_types: string[];
  psychological_triggers: string[];
  tone: string;
  clarifying_questions: ClarifyingQuestion[];
  similar_posts: string[];
}

export interface HookVariation {
  version: number;
  text: string;
  hook_type: string;
  score: number;
  reasoning: string;
}

export interface WriterOutput {
  hooks: HookVariation[];
  body_content: string;
  cta: string;
  hashtags: string[];
  formatting_metadata: {
    word_count: number;
    reading_time_seconds: number;
    line_count: number;
  };
}

export interface SlideSpec {
  slide_number: number;
  layout: string;
  headline: string;
  body_text: string | null;
  image_description: string | null;
  design_notes: string | null;
}

export interface VisualOutput {
  visual_specs: {
    total_slides: number;
    slides: SlideSpec[];
    overall_style: string;
    color_palette: string[];
    typography_notes: string;
  };
  image_prompts: string[];
}

export interface OptimizerOutput {
  decision: "APPROVE" | "REVISE";
  quality_score: number;
  brand_consistency_score: number;
  formatting_issues: string[];
  suggestions: string[];
  predicted_impressions_min: number;
  predicted_impressions_max: number;
  predicted_engagement_rate: number;
  confidence: number;
}

export interface FinalPost {
  format: "text" | "carousel" | "video";
  hook: HookVariation;
  body: string;
  cta: string;
  hashtags: string[];
  visual_specs: VisualOutput["visual_specs"] | null;
  quality_score: number;
  predicted_impressions: [number, number];
}

// === Agent State Types ===

export type AgentStatus = "pending" | "active" | "success" | "error" | "skipped";

export interface AgentExecution {
  status: AgentStatus;
  progress: number;
  thoughts: string[];
  execution_time_ms?: number;
  started_at?: number;
}

// === Generation Steps ===

export type GenerationStep = 
  | "input"
  | "validator"
  | "strategist"
  | "questions"
  | "writer"
  | "visual"
  | "optimizer"
  | "review";

export const STEP_ORDER: GenerationStep[] = [
  "input",
  "validator",
  "strategist",
  "questions",
  "writer",
  "visual",
  "optimizer",
  "review",
];

export const STEP_LABELS: Record<GenerationStep, string> = {
  input: "Your Idea",
  validator: "Validator",
  strategist: "Strategist",
  questions: "Questions",
  writer: "Writer",
  visual: "Visual",
  optimizer: "Optimizer",
  review: "Final Review",
};

// === Store State ===

interface GenerationState {
  // Current step
  currentStep: GenerationStep;
  
  // Input data
  rawIdea: string;
  preferredFormat: "text" | "carousel" | "video" | "auto";
  
  // API tracking
  postId: string | null;
  historyId: string | null;
  isGenerating: boolean;
  error: string | null;
  
  // Agent executions
  agents: {
    validator: AgentExecution;
    strategist: AgentExecution;
    writer: AgentExecution;
    visual: AgentExecution;
    optimizer: AgentExecution;
  };
  
  // Agent outputs
  validatorOutput: ValidatorOutput | null;
  strategistOutput: StrategistOutput | null;
  writerOutput: WriterOutput | null;
  visualOutput: VisualOutput | null;
  optimizerOutput: OptimizerOutput | null;
  
  // User answers to questions
  questionAnswers: Record<string, string>;
  
  // Final post
  finalPost: FinalPost | null;
  selectedHookIndex: number;
  
  // Actions
  setRawIdea: (idea: string) => void;
  setPreferredFormat: (format: "text" | "carousel" | "video" | "auto") => void;
  setCurrentStep: (step: GenerationStep) => void;
  goToNextStep: () => void;
  goToPreviousStep: () => void;
  
  // API tracking actions
  setPostId: (id: string | null) => void;
  setHistoryId: (id: string | null) => void;
  setIsGenerating: (status: boolean) => void;
  setError: (error: string | null) => void;
  
  updateAgentExecution: (agent: keyof GenerationState["agents"], update: Partial<AgentExecution>) => void;
  addAgentThought: (agent: keyof GenerationState["agents"], thought: string) => void;
  
  setValidatorOutput: (output: ValidatorOutput) => void;
  setStrategistOutput: (output: StrategistOutput) => void;
  setWriterOutput: (output: WriterOutput) => void;
  setVisualOutput: (output: VisualOutput) => void;
  setOptimizerOutput: (output: OptimizerOutput) => void;
  
  setQuestionAnswer: (questionId: string, answer: string) => void;
  setSelectedHookIndex: (index: number) => void;
  setFinalPost: (post: FinalPost) => void;
  
  resetGeneration: () => void;
}

const initialAgentState: AgentExecution = {
  status: "pending",
  progress: 0,
  thoughts: [],
};

const initialState = {
  currentStep: "input" as GenerationStep,
  rawIdea: "",
  preferredFormat: "auto" as const,
  postId: null as string | null,
  historyId: null as string | null,
  isGenerating: false,
  error: null as string | null,
  agents: {
    validator: { ...initialAgentState },
    strategist: { ...initialAgentState },
    writer: { ...initialAgentState },
    visual: { ...initialAgentState },
    optimizer: { ...initialAgentState },
  },
  validatorOutput: null,
  strategistOutput: null,
  writerOutput: null,
  visualOutput: null,
  optimizerOutput: null,
  questionAnswers: {},
  finalPost: null,
  selectedHookIndex: 0,
};

export const useGenerationStore = create<GenerationState>((set, get) => ({
  ...initialState,
  
  setRawIdea: (idea) => set({ rawIdea: idea }),
  setPreferredFormat: (format) => set({ preferredFormat: format }),
  setCurrentStep: (step) => set({ currentStep: step }),
  
  goToNextStep: () => {
    const { currentStep } = get();
    const currentIndex = STEP_ORDER.indexOf(currentStep);
    if (currentIndex < STEP_ORDER.length - 1) {
      set({ currentStep: STEP_ORDER[currentIndex + 1] });
    }
  },
  
  goToPreviousStep: () => {
    const { currentStep } = get();
    const currentIndex = STEP_ORDER.indexOf(currentStep);
    if (currentIndex > 0) {
      set({ currentStep: STEP_ORDER[currentIndex - 1] });
    }
  },
  
  // API tracking actions
  setPostId: (id) => set({ postId: id }),
  setHistoryId: (id) => set({ historyId: id }),
  setIsGenerating: (status) => set({ isGenerating: status }),
  setError: (error) => set({ error }),
  
  updateAgentExecution: (agent, update) => set((state) => ({
    agents: {
      ...state.agents,
      [agent]: { ...state.agents[agent], ...update },
    },
  })),
  
  addAgentThought: (agent, thought) => set((state) => ({
    agents: {
      ...state.agents,
      [agent]: {
        ...state.agents[agent],
        thoughts: [...state.agents[agent].thoughts, thought],
      },
    },
  })),
  
  setValidatorOutput: (output) => set({ validatorOutput: output }),
  setStrategistOutput: (output) => set({ strategistOutput: output }),
  setWriterOutput: (output) => set({ writerOutput: output }),
  setVisualOutput: (output) => set({ visualOutput: output }),
  setOptimizerOutput: (output) => set({ optimizerOutput: output }),
  
  setQuestionAnswer: (questionId, answer) => set((state) => ({
    questionAnswers: { ...state.questionAnswers, [questionId]: answer },
  })),
  
  setSelectedHookIndex: (index) => set({ selectedHookIndex: index }),
  setFinalPost: (post) => set({ finalPost: post }),
  
  resetGeneration: () => set({
    ...initialState,
    agents: {
      validator: { ...initialAgentState },
      strategist: { ...initialAgentState },
      writer: { ...initialAgentState },
      visual: { ...initialAgentState },
      optimizer: { ...initialAgentState },
    },
  }),
}));
