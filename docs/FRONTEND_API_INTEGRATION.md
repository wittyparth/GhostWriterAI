# LinkedIn AI Agent - Backend API Integration Guide

## 🔗 Complete API Reference for Frontend

This document maps **every frontend page** to the **exact backend endpoints** with request/response formats.

---

## 📡 Backend Base URL

```
Development: http://localhost:8000
Production: https://api.yourapp.com
```

---

## 🏥 Health & System Endpoints

### Check API Status

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": true,
  "cache": true,
  "llm": true,
  "version": "0.1.0"
}
```

**Frontend Usage:** Call on app startup to verify backend is running.

---

### Detailed Health Check

```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "components": [
    {"name": "database", "status": "healthy", "latency_ms": 5, "message": null},
    {"name": "cache", "status": "healthy", "latency_ms": 2, "message": "In-memory cache active"},
    {"name": "llm", "status": "healthy", "latency_ms": null, "message": "Gemini API configured"}
  ]
}
```

---

## 📝 Post Generation Endpoints (Core Feature)

### 1. Start Post Generation

```http
POST /api/v1/posts/generate
Content-Type: application/json
```

**Request Body:**
```typescript
interface IdeaInput {
  raw_idea: string;           // 10-5000 chars, required
  preferred_format?: "text" | "carousel" | "video" | "auto";  // default: "auto"
  content_pillar?: string;    // optional
}
```

**Example Request:**
```json
{
  "raw_idea": "3 lessons I learned from failing my first startup after 18 months and burning through $500K",
  "preferred_format": "auto"
}
```

**Response (Success):**
```typescript
interface ClarifyingQuestionsResponse {
  post_id: string;            // UUID - SAVE THIS!
  questions: ClarifyingQuestion[];
  original_idea: string;
}

interface ClarifyingQuestion {
  question_id: string;        // e.g., "q1", "q2"
  question: string;           // The question text
  rationale: string;          // Why this question matters
  required: boolean;          // Must be answered
}
```

**Example Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "question_id": "q1",
      "question": "What was the specific outcome or lesson from your startup failure?",
      "rationale": "Adds concrete details and credibility to your story",
      "required": true
    },
    {
      "question_id": "q2",
      "question": "What was your role in the startup?",
      "rationale": "Establishes authority and context",
      "required": true
    },
    {
      "question_id": "q3",
      "question": "What would you do differently if you could start again?",
      "rationale": "Creates valuable takeaways for readers",
      "required": false
    }
  ],
  "original_idea": "3 lessons I learned from failing my first startup..."
}
```

**Error Responses:**
- `422`: Validation error (idea too short, format invalid)
- `500`: Generation failed

**Frontend Flow:**
1. User enters idea → Call this endpoint
2. Store `post_id` in state/URL
3. Display questions to user
4. Wait for user answers

---

### 2. Submit Answers & Complete Generation

```http
POST /api/v1/posts/{post_id}/answers
Content-Type: application/json
```

**Request Body:**
```typescript
interface SubmitAnswersRequest {
  answers: QuestionAnswer[];
}

interface QuestionAnswer {
  question_id: string;   // Must match question_id from step 1
  answer: string;        // User's answer
}
```

**Example Request:**
```json
{
  "answers": [
    {"question_id": "q1", "answer": "The main lesson was about product-market fit - we built something nobody wanted"},
    {"question_id": "q2", "answer": "I was the co-founder and CEO"},
    {"question_id": "q3", "answer": "I would validate the idea with 50 customers before writing a single line of code"}
  ]
}
```

**Response (Success) - Full Generated Post:**
```typescript
interface GeneratedPostResponse {
  post_id: string;
  status: "completed";
  format: "text" | "carousel" | "video";
  structure_type: string;
  
  // Content
  hooks: HookVariation[];      // 3 hook options
  recommended_hook_index: number;
  body_content: string;
  cta: string;
  hashtags: string[];
  
  // For carousel format
  visual_specs?: VisualSpecs;
  
  // Quality metrics
  quality_score: number;          // 0-10
  brand_consistency_score: number; // 0-10
  predicted_impressions?: [number, number]; // [min, max]
  predicted_engagement_rate?: number;       // e.g., 0.045 = 4.5%
  
  optimization_suggestions: string[];
}

interface HookVariation {
  version: number;        // 1, 2, or 3
  text: string;           // The hook text
  hook_type: string;      // e.g., "personal_story", "data_shock"
  score: number;          // 0-10
  reasoning: string;      // Why this hook works
}

interface VisualSpecs {
  total_slides: number;
  slides: VisualSlide[];
  overall_style: string;
  color_palette: string[];
  typography_notes?: string;
}

interface VisualSlide {
  slide_number: number;
  layout: string;
  headline: string;
  body_text?: string;
  image_description?: string;
  design_notes?: string;
}
```

**Example Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "format": "text",
  "structure_type": "story_post",
  "hooks": [
    {
      "version": 1,
      "text": "I burned through $500K before learning this one lesson.",
      "hook_type": "personal_story",
      "score": 8.7,
      "reasoning": "Strong emotional opening with specific number"
    },
    {
      "version": 2,
      "text": "My startup died after 18 months. Here's why I'm grateful.",
      "hook_type": "contrarian",
      "score": 8.2,
      "reasoning": "Unexpected twist creates curiosity"
    },
    {
      "version": 3,
      "text": "The $500K mistake that changed how I think about startups:",
      "hook_type": "data_shock",
      "score": 7.9,
      "reasoning": "Leads with the cost, creates curiosity gap"
    }
  ],
  "recommended_hook_index": 0,
  "body_content": "In 2022, I was convinced we had the next big thing...\n\n[Full post body here]",
  "cta": "What's the biggest lesson you've learned from failure? 👇",
  "hashtags": ["startup", "entrepreneurship", "failure", "lessons", "founder"],
  "quality_score": 8.5,
  "brand_consistency_score": 8.0,
  "predicted_impressions": [5000, 15000],
  "predicted_engagement_rate": 0.045,
  "optimization_suggestions": [
    "Consider adding a specific metric to strengthen credibility",
    "The CTA could be more specific to encourage comments"
  ]
}
```

---

### 3. Check Generation Status

```http
GET /api/v1/posts/{post_id}/status
```

**Response:**
```typescript
interface GenerationStatusResponse {
  post_id: string;
  status: "pending" | "processing" | "awaiting_answers" | "completed" | "failed";
  current_agent?: string;          // "validator", "strategist", "writer", "optimizer"
  progress_percent: number;        // 0-100
  estimated_seconds_remaining?: number;
}
```

**Example:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "current_agent": "writer",
  "progress_percent": 60,
  "estimated_seconds_remaining": 15
}
```

**Frontend Usage:** Poll this endpoint every 2 seconds during generation to show progress.

---

### 4. Get Single Post

```http
GET /api/v1/posts/{post_id}
```

**Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "raw_idea": "3 lessons from failing my startup",
  "status": "completed",
  "format": "text",
  "final_content": "I burned through $500K...",
  "quality_score": 8.5,
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

### 5. List All Posts

```http
GET /api/v1/posts?limit=20&offset=0
```

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 20 | Max posts to return |
| offset | int | 0 | Pagination offset |

**Response:**
```json
{
  "posts": [
    {
      "post_id": "550e8400-e29b-41d4-a716-446655440000",
      "raw_idea": "3 lessons from failing my startup",
      "status": "completed",
      "format": "text",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

---

## 📄 Frontend Page → Backend Mapping

### Landing Page (`/`)
**No backend calls required** - Static marketing page

---

### Login Page (`/login`)
**Backend endpoints needed:**
```
POST /auth/login  (TO BE IMPLEMENTED)
```

**Temporary workaround:** Use local storage mock auth until backend auth is added.

---

### Dashboard (`/app/dashboard`)

**API Calls on Load:**
```typescript
// 1. Get recent posts
const recentPosts = await fetch('/api/v1/posts?limit=5');

// 2. Get health status (optional)
const health = await fetch('/health');
```

**Display Data:**
- Recent posts list
- Total posts count
- Status summary

---

### Post Generator (`/app/generate`) - MAIN FLOW

**Step-by-Step API Flow:**

```typescript
// STEP 1: User enters idea, click Generate
const response = await fetch('/api/v1/posts/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ raw_idea: userIdea })
});
const { post_id, questions } = await response.json();

// STEP 2: Display questions to user, collect answers

// STEP 3: Submit answers
const result = await fetch(`/api/v1/posts/${post_id}/answers`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ answers: userAnswers })
});
const generatedPost = await result.json();

// STEP 4: Display generated post with hook options
```

**TanStack Query Implementation:**
```typescript
// hooks/usePostGeneration.ts

export function useGeneratePost() {
  return useMutation({
    mutationFn: async (idea: string) => {
      const res = await api.post('/api/v1/posts/generate', { raw_idea: idea });
      return res.data;
    },
  });
}

export function useSubmitAnswers() {
  return useMutation({
    mutationFn: async ({ postId, answers }: { postId: string; answers: Answer[] }) => {
      const res = await api.post(`/api/v1/posts/${postId}/answers`, { answers });
      return res.data;
    },
  });
}

export function usePostStatus(postId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['post-status', postId],
    queryFn: async () => {
      const res = await api.get(`/api/v1/posts/${postId}/status`);
      return res.data;
    },
    enabled,
    refetchInterval: 2000, // Poll every 2 seconds
  });
}
```

---

### Post History (`/app/posts`)

**API Calls:**
```typescript
// List posts with pagination
const { data } = useQuery({
  queryKey: ['posts', { limit, offset }],
  queryFn: () => api.get(`/api/v1/posts?limit=${limit}&offset=${offset}`),
});
```

---

### Post Detail (`/app/posts/:postId`)

**API Calls:**
```typescript
const { data: post } = useQuery({
  queryKey: ['post', postId],
  queryFn: () => api.get(`/api/v1/posts/${postId}`),
});
```

---

## 🔄 Real-Time Generation Progress

The post generator should show live agent progress. Here's how to implement:

```typescript
// PostGenerator.tsx - Generation Step

function GenerationStep({ postId }: { postId: string }) {
  const [currentAgent, setCurrentAgent] = useState<string>('validator');
  const [progress, setProgress] = useState(0);
  
  // Poll status every 2 seconds
  const { data: status } = useQuery({
    queryKey: ['post-status', postId],
    queryFn: () => api.get(`/api/v1/posts/${postId}/status`),
    refetchInterval: 2000,
    enabled: !!postId,
  });
  
  useEffect(() => {
    if (status) {
      setCurrentAgent(status.current_agent);
      setProgress(status.progress_percent);
      
      if (status.status === 'completed') {
        // Move to next step
        onComplete();
      }
    }
  }, [status]);
  
  const agents = [
    { id: 'validator', name: 'Validator', icon: Shield, desc: 'Checking idea quality' },
    { id: 'strategist', name: 'Strategist', icon: Lightbulb, desc: 'Planning content structure' },
    { id: 'writer', name: 'Writer', icon: PenTool, desc: 'Crafting your content' },
    { id: 'optimizer', name: 'Optimizer', icon: Zap, desc: 'Polishing for engagement' },
  ];
  
  return (
    <div className="space-y-6">
      {agents.map((agent, i) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          status={
            agent.id === currentAgent ? 'active' :
            agents.findIndex(a => a.id === currentAgent) > i ? 'complete' : 'pending'
          }
          progress={agent.id === currentAgent ? progress : 0}
        />
      ))}
    </div>
  );
}
```

---

## 📦 TypeScript Types (Copy to Frontend)

```typescript
// types/api.ts

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
  status: string;
  format?: string;
  created_at: string;
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
```

---

## ⚠️ Error Handling

```typescript
// lib/api.ts

import axios, { AxiosError } from 'axios';

export interface ApiError {
  detail: string;
  error_code?: string;
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    const message = error.response?.data?.detail || 'An error occurred';
    
    // Handle specific errors
    if (error.response?.status === 422) {
      // Validation error - show form errors
      toast.error('Please check your input');
    } else if (error.response?.status === 429) {
      // Rate limited
      toast.error('Too many requests. Please wait a moment.');
    } else if (error.response?.status === 500) {
      // Server error
      toast.error('Something went wrong. Please try again.');
    }
    
    return Promise.reject(error);
  }
);
```

---

## 🎯 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER JOURNEY                                  │
└─────────────────────────────────────────────────────────────────────┘

Landing Page (/)
      │
      ▼ [Click "Get Started"]
      │
Login/Signup (/login, /signup)
      │
      ▼ [Authenticated]
      │
Dashboard (/app/dashboard)
      │  └── GET /api/v1/posts?limit=5 (recent posts)
      │
      ▼ [Click "Create New Post"]
      │
┌─────────────────────────────────────────────────────────────────────┐
│                    POST GENERATOR (/app/generate)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Step 1: Enter Idea                                                  │
│      │                                                               │
│      ▼ POST /api/v1/posts/generate                                   │
│      │  Body: { raw_idea: "..." }                                    │
│      │  Response: { post_id, questions[] }                           │
│      │                                                               │
│  Step 2: Answer Questions                                            │
│      │  (Show questions from response)                               │
│      │                                                               │
│      ▼ POST /api/v1/posts/{post_id}/answers                          │
│      │  Body: { answers: [...] }                                     │
│      │                                                               │
│  Step 3: Generation Progress                                         │
│      │  Poll: GET /api/v1/posts/{post_id}/status                     │
│      │  Show: current_agent, progress_percent                        │
│      │                                                               │
│  Step 4: Review & Select Hook                                        │
│      │  (Display hooks[] from generation response)                   │
│      │                                                               │
│  Step 5: Final Output                                                │
│      │  (Copy, save, share)                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼ [View History]
      │
Post History (/app/posts)
      │  └── GET /api/v1/posts?limit=20&offset=0
      │
      ▼ [Click on post]
      │
Post Detail (/app/posts/:id)
         └── GET /api/v1/posts/{post_id}
```

---

## 🔧 Environment Variables

Create `.env` in frontend:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Feature Flags
VITE_ENABLE_ANALYTICS=true

# App Info
VITE_APP_NAME="LinkedIn AI Agent"
VITE_APP_VERSION="0.1.0"
```

---

This document ensures the frontend perfectly aligns with the backend API!
