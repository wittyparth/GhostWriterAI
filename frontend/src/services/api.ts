// Backend API Configuration
import { API_BASE_URL, ApiError } from './config';
import { authFetch } from './auth';

export { API_BASE_URL };

// ============ Types ============

export interface IdeaInput {
  raw_idea: string;
  preferred_format?: 'text' | 'carousel' | 'video' | 'auto';
  content_pillar?: string;
}

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

export interface GeneratedPost {
  post_id: string;
  status: string;
  post?: {
    format: string;
    hook: HookVariation;
    body: string;
    cta: string;
    hashtags: string[];
    visual_specs?: any;
    quality_score: number;
    predicted_impressions: [number, number];
  };
  quality_score?: number;
  predicted_engagement?: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  database: boolean;
  cache: boolean;
  llm: boolean;
  version: string;
}

// History API Types
export interface GenerationHistoryListItem {
  history_id: string;
  post_id: string;
  raw_idea: string;
  status: string;
  format?: string;
  quality_score?: number;
  total_execution_time_ms?: number;
  started_at: string;
  completed_at?: string;
}

export interface GenerationHistoryListResponse {
  histories: GenerationHistoryListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface AgentOutputSummary {
  agent_name: string;
  status: string;
  execution_time_ms: number;
  decision?: string;
  score?: number;
  summary?: string;
  has_output: boolean;
}

export interface GenerationEvent {
  event_id: string;
  event_type: string;
  agent_name: string;
  message: string;
  execution_time_ms: number;
  progress_percent: number;
  output_summary?: string;
  decision?: string;
  score?: number;
  event_data: Record<string, any>;
  error_message?: string;
  retry_attempt?: number;
  timestamp: string;
}

export interface GenerationHistoryDetail {
  history_id: string;
  post_id: string;
  raw_idea: string;
  preferred_format?: string;
  brand_profile_snapshot: Record<string, any>;
  validator_output: Record<string, any>;
  strategist_output: Record<string, any>;
  writer_output: Record<string, any>;
  visual_output: Record<string, any>;
  optimizer_output: Record<string, any>;
  clarifying_questions: ClarifyingQuestion[];
  user_answers: Record<string, string>;
  final_post: Record<string, any>;
  selected_hook_index: number;
  status: string;
  total_execution_time_ms?: number;
  revision_count: number;
  validator_time_ms?: number;
  strategist_time_ms?: number;
  writer_time_ms?: number;
  visual_time_ms?: number;
  optimizer_time_ms?: number;
  error_message?: string;
  failed_agent?: string;
  started_at: string;
  phase1_completed_at?: string;
  answers_submitted_at?: string;
  completed_at?: string;
  events: GenerationEvent[];
  agents_summary: AgentOutputSummary[];
}

// ============ API Client ============

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  return authFetch<T>(endpoint, options);
}

// ============ API Functions ============

/**
 * Generate a new post (non-streaming)
 */
export async function generatePost(input: IdeaInput): Promise<ClarifyingQuestionsResponse> {
  return fetchApi<ClarifyingQuestionsResponse>('/api/v1/posts/generate', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

/**
 * Submit answers to clarifying questions (non-streaming)
 */
export async function submitAnswers(
  postId: string,
  answers: Array<{ question_id: string; answer: string }>
): Promise<GeneratedPost> {
  return fetchApi<GeneratedPost>(`/api/v1/posts/${postId}/answers`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  });
}

/**
 * Get list of generation histories
 */
export async function getHistoryList(
  limit: number = 20,
  offset: number = 0
): Promise<GenerationHistoryListResponse> {
  return fetchApi<GenerationHistoryListResponse>(
    `/api/v1/history/?limit=${limit}&offset=${offset}`
  );
}

/**
 * Get complete generation history detail
 */
export async function getHistoryDetail(historyId: string): Promise<GenerationHistoryDetail> {
  return fetchApi<GenerationHistoryDetail>(`/api/v1/history/${historyId}`);
}

/**
 * Get generation history by post ID
 */
export async function getHistoryByPostId(postId: string): Promise<GenerationHistoryDetail> {
  return fetchApi<GenerationHistoryDetail>(`/api/v1/history/post/${postId}`);
}

/**
 * Get specific agent output
 */
export async function getAgentOutput(
  historyId: string,
  agentName: string
): Promise<{ history_id: string; agent_name: string; output: any; summary?: string }> {
  return fetchApi(`/api/v1/history/${historyId}/agent/${agentName}`);
}

/**
 * Update selected hook index
 */
export async function updateSelectedHook(
  historyId: string,
  hookIndex: number
): Promise<{ status: string }> {
  return fetchApi(`/api/v1/history/${historyId}/selected-hook?hook_index=${hookIndex}`, {
    method: 'PATCH',
  });
}

/**
 * Health check
 */
export async function healthCheck(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>('/health');
}

/**
 * Get post status
 */
export async function getPostStatus(postId: string): Promise<{
  post_id: string;
  status: string;
  current_agent?: string;
  progress_percent: number;
}> {
  return fetchApi(`/api/v1/posts/${postId}/status`);
}

/**
 * Get aggregated analytics stats
 */
export async function getAnalyticsStats(): Promise<AnalyticsResponse> {
  return fetchApi<AnalyticsResponse>('/api/v1/history/stats');
}

export { ApiError };

// ============ Analytics Types ============

export interface AnalyticsStats {
  total_posts: number;
  completed_posts: number;
  avg_quality_score: number;
  posts_this_week: number;
}

export interface AnalyticsChartData {
  date: string;
  count: number;
  avg_score: number;
}

export interface AnalyticsResponse {
  stats: AnalyticsStats;
  daily_activity: AnalyticsChartData[];
  format_distribution: Array<{ name: string; value: number }>;
  status_distribution: Array<{ status: string; count: number }>;
  top_posts: Array<{ idea: string; score: number; status: string }>;
}
