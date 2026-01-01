// API Types based on backend specification

// ============ Request Types ============

export interface IdeaInput {
  raw_idea: string;
  preferred_format?: 'text' | 'carousel' | 'video' | 'auto';
  content_pillar?: string;
}

export interface SubmitAnswersRequest {
  answers: QuestionAnswer[];
}

export interface QuestionAnswer {
  question_id: string;
  answer: string;
}

// ============ Response Types ============

export interface ClarifyingQuestion {
  question_id: string;
  question: string;
  rationale: string;
  required: boolean;
}

export interface ClarifyingQuestionsResponse {
  post_id: string;
  questions: ClarifyingQuestion[];
  original_idea: string;
}

export interface HookVariation {
  version: number;
  text: string;
  hook_type: string;
  score: number;
  reasoning: string;
}

export interface VisualSlide {
  slide_number: number;
  layout: string;
  headline: string;
  body_text?: string;
  image_description?: string;
  design_notes?: string;
}

export interface VisualSpecs {
  total_slides: number;
  slides: VisualSlide[];
  overall_style: string;
  color_palette: string[];
  typography_notes?: string;
}

export interface GeneratedPost {
  post_id: string;
  status: 'completed';
  format: 'text' | 'carousel' | 'video';
  structure_type: string;
  hooks: HookVariation[];
  recommended_hook_index: number;
  body_content: string;
  cta: string;
  hashtags: string[];
  visual_specs?: VisualSpecs;
  quality_score: number;
  brand_consistency_score: number;
  predicted_impressions?: [number, number];
  predicted_engagement_rate?: number;
  optimization_suggestions: string[];
}

export interface GenerationStatus {
  post_id: string;
  status: 'pending' | 'processing' | 'awaiting_answers' | 'completed' | 'failed';
  current_agent?: string;
  progress_percent: number;
  estimated_seconds_remaining?: number;
}

export interface PostSummary {
  post_id: string;
  raw_idea: string;
  status: 'pending' | 'processing' | 'awaiting_answers' | 'completed' | 'failed';
  format?: 'text' | 'carousel' | 'video';
  quality_score?: number;
  created_at: string;
  final_content?: string;
}

export interface PostListResponse {
  posts: PostSummary[];
  count: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  database: boolean;
  cache: boolean;
  llm: boolean;
  version: string;
}

// Brand Profile Types
export interface ContentPillar {
  id: string;
  name: string;
  description: string;
  color: string;
}

export interface BrandProfile {
  id: string;
  name: string;
  title: string;
  avatar_url?: string;
  bio?: string;
  content_pillars: ContentPillar[];
  target_audience: string;
  voice_tone: {
    formality: number; // 0-100
    humor: number;
    emotion: number;
    technicality: number;
  };
  sample_posts?: string[];
}

// User & Auth Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  plan: 'free' | 'pro' | 'enterprise';
  created_at: string;
}
