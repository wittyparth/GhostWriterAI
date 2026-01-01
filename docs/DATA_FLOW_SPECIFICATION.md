# LinkedIn AI Agent - Complete Data Flow & API Specification

## Document Purpose
This document provides the **complete technical specification** of data flow, API responses, events, and available data at each step. Use this to build the frontend UI.

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Complete User Flow](#2-complete-user-flow)
3. [API Endpoints Specification](#3-api-endpoints-specification)
4. [Streaming Events Specification](#4-streaming-events-specification)
5. [Agent Output Data Structures](#5-agent-output-data-structures)
6. [State Machine](#6-state-machine)
7. [Error Handling](#7-error-handling)

---

## 1. System Overview

### 1.1 Architecture
```
User Input → API → Orchestrator → [5 Agents in sequence] → Final Output
                        ↓
              Streaming Events (SSE) → Frontend
```

### 1.2 The 5 Agents (in order)
| Order | Agent | Purpose | When Skipped |
|-------|-------|---------|--------------|
| 1 | Validator | Validates idea quality | Never |
| 2 | Strategist | Creates content strategy + questions | Never |
| 3 | Writer | Generates post content | Never |
| 4 | Visual | Creates carousel specs | If format != "carousel" |
| 5 | Optimizer | Quality assurance + predictions | Never |

### 1.3 Two-Phase Execution
**Phase 1**: Validator → Strategist → PAUSE (wait for user answers)
**Phase 2**: Writer → Visual (optional) → Optimizer → Finalize

---

## 2. Complete User Flow

### Step 1: User Submits Idea

**User Action**: Enter raw idea text and optionally select format preference

**Input Data Available**:
```typescript
interface IdeaInput {
  raw_idea: string;           // Required, 10-5000 characters
  preferred_format?: "text" | "carousel" | "video" | "auto";  // Default: "auto"
  content_pillar?: string;    // Optional category
}
```

**Example**:
```json
{
  "raw_idea": "3 lessons I learned from failing my first startup",
  "preferred_format": "auto"
}
```

---

### Step 2: Phase 1 Execution (Validator + Strategist)

**What Happens**:
1. System generates a unique `post_id` (UUID)
2. Validator agent analyzes the idea
3. If REJECTED → Flow ends with rejection details
4. If APPROVED → Strategist agent runs
5. Strategist generates clarifying questions
6. System pauses, waits for user answers

**Duration**: Typically 2-5 seconds total

---

### Step 3: User Answers Questions

**User Action**: Answer each clarifying question from Strategist

**Data Available**:
```typescript
interface ClarifyingQuestion {
  question_id: string;      // e.g., "q1", "q2"
  question: string;         // The question text
  rationale: string;        // Why this question matters
  required: boolean;        // Must be answered
}
```

**User Provides**:
```typescript
interface QuestionAnswer {
  question_id: string;
  answer: string;
}
```

---

### Step 4: Phase 2 Execution (Writer → Visual → Optimizer)

**What Happens**:
1. Writer generates 3 hook variations + body + CTA + hashtags
2. If format is "carousel" → Visual agent creates slide specs
3. Optimizer evaluates quality and predicts performance
4. If Optimizer says "REVISE" → Loop back to Writer (max 2 times)
5. Finalize compiles the final post

**Duration**: Typically 5-15 seconds total

---

### Step 5: Final Output Displayed

**User Sees**: Complete generated post with all metadata

---

## 3. API Endpoints Specification

### 3.1 Start Generation (Non-Streaming)

**Endpoint**: `POST /api/v1/posts/generate`

**Request Body**:
```json
{
  "raw_idea": "3 lessons I learned from failing my first startup",
  "preferred_format": "auto"
}
```

**Success Response** (Status 200):
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "question_id": "q1",
      "question": "What was the specific financial or time outcome?",
      "rationale": "Concrete numbers add credibility and emotional impact",
      "required": true
    },
    {
      "question_id": "q2",
      "question": "What industry was your startup in?",
      "rationale": "Helps tailor content to your target audience",
      "required": false
    },
    {
      "question_id": "q3",
      "question": "Who was your target customer?",
      "rationale": "Makes the story more relatable",
      "required": false
    }
  ],
  "original_idea": "3 lessons I learned from failing my first startup"
}
```

**Rejection Response** (Status 422):
```json
{
  "detail": {
    "status": "rejected",
    "reason": "The idea lacks specificity and unique angle. Generic startup advice won't perform well.",
    "quality_score": 4.2,
    "suggestions": [
      "Add a specific personal story or data point",
      "Focus on one unique insight rather than generic lessons",
      "Consider a controversial or surprising angle"
    ]
  }
}
```

---

### 3.2 Start Generation (Streaming)

**Endpoint**: `POST /api/v1/posts/generate/stream`

**Request Body**: Same as above

**Response**: Server-Sent Events (SSE) stream

**Response Headers**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Post-ID: 550e8400-e29b-41d4-a716-446655440000
```

See Section 4 for event details.

---

### 3.3 Submit Answers (Non-Streaming)

**Endpoint**: `POST /api/v1/posts/{post_id}/answers`

**Request Body**:
```json
{
  "answers": [
    {"question_id": "q1", "answer": "We lost $50,000 and shut down after 18 months"},
    {"question_id": "q2", "answer": "B2B SaaS for restaurants"},
    {"question_id": "q3", "answer": "Small restaurant owners"}
  ]
}
```

**Success Response** (Status 200):
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "post": {
    "format": "text",
    "hook": {
      "version": 1,
      "text": "I lost $50,000 and 18 months of my life.",
      "hook_type": "personal_story",
      "score": 9.0,
      "reasoning": "Strong emotional impact with specific numbers"
    },
    "body": "Here's what I learned building (and failing) a B2B SaaS for restaurants:\n\n1️⃣ Validate before you build\nWe spent 6 months building features no one asked for.\nTalk to 100 potential customers first.\n\n2️⃣ Cash is oxygen\nWe ran out of runway with promising deals in the pipeline.\nAlways keep 6 months of buffer.\n\n3️⃣ Fail fast, learn faster\nThe failure taught me more than any MBA ever could.",
    "cta": "What's the biggest lesson failure has taught you?",
    "hashtags": ["startup", "entrepreneurship", "failure", "lessons"],
    "visual_specs": null,
    "quality_score": 8.5,
    "predicted_impressions": [5000, 15000]
  },
  "quality_score": 8.5,
  "predicted_engagement": 0.045
}
```

---

### 3.4 Submit Answers (Streaming)

**Endpoint**: `POST /api/v1/posts/{post_id}/answers/stream`

**Request Body**:
```json
{
  "q1": "We lost $50,000 and shut down after 18 months",
  "q2": "B2B SaaS for restaurants",
  "q3": "Small restaurant owners"
}
```

**Response**: Server-Sent Events (SSE) stream. See Section 4.

---

### 3.5 Get Agent Thoughts

**Endpoint**: `GET /api/v1/posts/{post_id}/agents`

**Response**:
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_execution_time_ms": 8542,
  "revision_count": 0,
  "agents": {
    "validator": {
      "agent_name": "validator",
      "status": "success",
      "execution_time_ms": 1234,
      "attempt": 1,
      "timestamp": "2026-01-01T14:30:00.000Z",
      "output_summary": "Decision: APPROVE | Quality Score: 8.5/10",
      "decision": "APPROVE",
      "score": 8.5,
      "full_output": { ... }
    },
    "strategist": { ... },
    "writer": { ... },
    "optimizer": { ... }
  },
  "execution_log": [
    {
      "agent_name": "validator",
      "status": "success",
      "execution_time_ms": 1234,
      "timestamp": "2026-01-01T14:30:00.000Z",
      "output_summary": "Decision: APPROVE | Quality Score: 8.5/10"
    },
    ...
  ]
}
```

---

### 3.6 Get Execution Log

**Endpoint**: `GET /api/v1/posts/{post_id}/execution-log`

**Response**:
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "events": [
    {
      "event_type": "agent_start",
      "agent_name": "validator",
      "message": "🔄 Validator agent is analyzing...",
      "timestamp": "2026-01-01T14:30:00.000Z",
      "execution_time_ms": 0,
      "data": {},
      "progress_percent": 5
    },
    {
      "event_type": "agent_complete",
      "agent_name": "validator",
      "message": "✅ Validator completed in 1234ms",
      "timestamp": "2026-01-01T14:30:01.234Z",
      "execution_time_ms": 1234,
      "data": {
        "summary": "Decision: APPROVE | Quality Score: 8.5/10",
        "decision": "APPROVE",
        "score": 8.5,
        "output": { ... }
      },
      "progress_percent": 15
    },
    ...
  ],
  "agent_outputs": {
    "validator": {
      "summary": "Decision: APPROVE | Quality Score: 8.5/10",
      "output": { ... }
    },
    ...
  }
}
```

---

### 3.7 Get Post Status

**Endpoint**: `GET /api/v1/posts/{post_id}/status`

**Response**:
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "awaiting_answers",
  "current_agent": "strategist",
  "progress_percent": 30,
  "estimated_seconds_remaining": 10
}
```

**Status Values**:
- `pending` - Not started
- `processing` - Agent is running
- `awaiting_answers` - Waiting for user to answer questions
- `completed` - All agents done, post ready
- `failed` - Error occurred

---

## 4. Streaming Events Specification

### 4.1 Event Types

| Event Type | When Emitted | Contains |
|------------|--------------|----------|
| `agent_start` | Agent begins processing | Agent name, message |
| `agent_complete` | Agent finished successfully | Full output, summary, scores |
| `agent_error` | Agent encountered error | Error message, retry info |
| `status_update` | General progress update | Message, progress % |
| `complete` | All agents done | Final post or questions |

---

### 4.2 Event: agent_start

**When**: An agent begins execution

**Payload**:
```json
{
  "event_type": "agent_start",
  "agent_name": "validator",
  "message": "🔄 Validator agent is analyzing...",
  "timestamp": "2026-01-01T14:30:00.000Z",
  "execution_time_ms": 0,
  "data": {},
  "progress_percent": 5
}
```

**Progress Percent by Agent**:
- validator start: 5
- strategist start: 20
- writer start: 45
- visual start: 65
- optimizer start: 80

---

### 4.3 Event: agent_complete

**When**: An agent finishes successfully

**Payload Structure**:
```json
{
  "event_type": "agent_complete",
  "agent_name": "validator",
  "message": "✅ Validator completed in 1234ms",
  "timestamp": "2026-01-01T14:30:01.234Z",
  "execution_time_ms": 1234,
  "data": {
    "summary": "Decision: APPROVE | Quality Score: 8.5/10",
    "decision": "APPROVE",
    "score": 8.5,
    "output": { ... full agent output ... }
  },
  "progress_percent": 15
}
```

**Progress Percent by Agent**:
- validator complete: 15
- strategist complete: 30
- writer complete: 55
- visual complete: 75
- optimizer complete: 90

---

### 4.4 Event: agent_error

**When**: An agent fails (will usually retry)

**Payload**:
```json
{
  "event_type": "agent_error",
  "agent_name": "writer",
  "message": "❌ Writer failed (attempt 1): Rate limit exceeded",
  "timestamp": "2026-01-01T14:30:05.000Z",
  "execution_time_ms": 0,
  "data": {
    "error": "Rate limit exceeded",
    "attempt": 1,
    "max_attempts": 3,
    "will_retry": true
  },
  "progress_percent": 45
}
```

---

### 4.5 Event: status_update

**When**: General progress update (revisions, etc.)

**Payload**:
```json
{
  "event_type": "status_update",
  "agent_name": "system",
  "message": "Revision 1 - improving content...",
  "timestamp": "2026-01-01T14:30:10.000Z",
  "execution_time_ms": 0,
  "data": {
    "revision_count": 1,
    "reason": "Optimizer requested revision for better hook"
  },
  "progress_percent": 60
}
```

---

### 4.6 Event: complete

**When**: All processing done

**Payload (Phase 1 - Awaiting Answers)**:
```json
{
  "event_type": "complete",
  "agent_name": "system",
  "message": "Ready for your answers to clarifying questions",
  "timestamp": "2026-01-01T14:30:02.500Z",
  "execution_time_ms": 2500,
  "data": {
    "status": "awaiting_answers",
    "post_id": "550e8400-e29b-41d4-a716-446655440000",
    "questions": [
      {
        "question_id": "q1",
        "question": "What was the specific outcome?",
        "rationale": "Adds credibility",
        "required": true
      }
    ],
    "original_idea": "3 lessons I learned from failing my first startup"
  },
  "progress_percent": 30
}
```

**Payload (Phase 2 - Fully Complete)**:
```json
{
  "event_type": "complete",
  "agent_name": "system",
  "message": "🎉 Post generation complete!",
  "timestamp": "2026-01-01T14:30:15.000Z",
  "execution_time_ms": 12500,
  "data": {
    "status": "completed",
    "post_id": "550e8400-e29b-41d4-a716-446655440000",
    "final_post": { ... see section 5.6 ... },
    "quality_score": 8.5,
    "execution_summary": { ... }
  },
  "progress_percent": 100
}
```

---

## 5. Agent Output Data Structures

### 5.1 Validator Agent Output

```typescript
interface ValidatorOutput {
  decision: "APPROVE" | "REFINE" | "REJECT";
  quality_score: number;           // 0-10
  brand_alignment_score: number;   // 0-10
  reasoning: string;               // Why this decision
  concerns: string[];              // List of concerns
  refinement_suggestions: string[]; // How to improve
}
```

**Example**:
```json
{
  "decision": "APPROVE",
  "quality_score": 8.5,
  "brand_alignment_score": 7.0,
  "reasoning": "This idea has strong tactical value with a personal narrative element that typically performs well on LinkedIn. The failure-to-lessons framework is proven to drive engagement.",
  "concerns": [
    "May need more specificity on the 'lessons' to avoid generic advice",
    "Consider adding a unique angle or contrarian view"
  ],
  "refinement_suggestions": [
    "Include specific numbers (money lost, time spent)",
    "Add one unexpected or counterintuitive lesson"
  ]
}
```

---

### 5.2 Strategist Agent Output

```typescript
interface StrategistOutput {
  recommended_format: "text" | "carousel" | "video";
  format_reasoning: string;
  structure_type: string;           // e.g., "story_post", "list_post"
  hook_types: string[];             // e.g., ["personal_story", "data_shock"]
  psychological_triggers: string[]; // e.g., ["curiosity_gap", "social_proof"]
  tone: string;                     // e.g., "conversational", "authoritative"
  clarifying_questions: ClarifyingQuestion[];
  similar_posts: string[];          // Reference examples
}

interface ClarifyingQuestion {
  question_id: string;
  question: string;
  rationale: string;
  required: boolean;
}
```

**Example**:
```json
{
  "recommended_format": "text",
  "format_reasoning": "Personal failure stories work best as text posts because they feel more authentic and personal. Carousel would feel too 'polished' for this vulnerable topic.",
  "structure_type": "story_post",
  "hook_types": ["personal_story", "vulnerability", "numbers"],
  "psychological_triggers": ["curiosity_gap", "relatability", "aspiration"],
  "tone": "conversational",
  "clarifying_questions": [
    {
      "question_id": "q1",
      "question": "What was the specific financial or time outcome of the failure?",
      "rationale": "Concrete numbers create emotional impact and credibility",
      "required": true
    },
    {
      "question_id": "q2",
      "question": "What industry was your startup in?",
      "rationale": "Context helps readers relate to your story",
      "required": false
    },
    {
      "question_id": "q3",
      "question": "What's one thing you would do differently?",
      "rationale": "Actionable insight increases save rate",
      "required": true
    },
    {
      "question_id": "q4",
      "question": "Did this failure lead to any unexpected positive outcomes?",
      "rationale": "Redemption arc increases engagement",
      "required": false
    }
  ],
  "similar_posts": []
}
```

---

### 5.3 Writer Agent Output

```typescript
interface WriterOutput {
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

interface HookVariation {
  version: number;        // 1, 2, or 3
  text: string;           // The actual hook text
  hook_type: string;      // e.g., "personal_story"
  score: number;          // 0-10 quality score
  reasoning: string;      // Why this hook works
}
```

**Example**:
```json
{
  "hooks": [
    {
      "version": 1,
      "text": "I lost $50,000 and 18 months of my life.",
      "hook_type": "personal_story",
      "score": 9.0,
      "reasoning": "Leads with specific numbers and emotional vulnerability. Creates immediate curiosity about what happened."
    },
    {
      "version": 2,
      "text": "My first startup failed spectacularly.\n\nBut it gave me the 3 most valuable lessons I've ever learned.",
      "hook_type": "contrast",
      "score": 8.2,
      "reasoning": "Classic failure-to-success setup. The word 'spectacularly' adds drama."
    },
    {
      "version": 3,
      "text": "18 months.\n$50,000.\n1 failed startup.\n\nAnd the best education money couldn't buy.",
      "hook_type": "list_format",
      "score": 7.8,
      "reasoning": "Uses LinkedIn-friendly formatting with short punchy lines. Less emotional but very scannable."
    }
  ],
  "body_content": "Here's what I learned building (and failing) a B2B SaaS for restaurants:\n\n1️⃣ Validate before you build\n\nWe spent 6 months building features no one asked for.\n\nI was so excited about my solution that I forgot to check if anyone had the problem.\n\n→ Talk to 100 potential customers before writing a single line of code.\n\n2️⃣ Cash is oxygen\n\nWe ran out of runway with promising deals in the pipeline.\n\n2 weeks. That's how close we were to closing our first big customer.\n\n→ Always keep 6 months of buffer. Always.\n\n3️⃣ Fail fast, learn faster\n\nThe failure taught me more than any MBA ever could.\n\nI learned about sales, about resilience, about picking myself up.\n\nAnd 2 years later, those lessons helped me build a company that actually worked.",
  "cta": "What's the biggest lesson failure has taught you?\n\n↓ Share in the comments",
  "hashtags": ["startup", "entrepreneurship", "failure", "founder", "lessons"],
  "formatting_metadata": {
    "word_count": 178,
    "reading_time_seconds": 45,
    "line_count": 28
  }
}
```

---

### 5.4 Visual Agent Output (Carousel Only)

```typescript
interface VisualOutput {
  visual_specs: {
    total_slides: number;
    slides: SlideSpec[];
    overall_style: string;
    color_palette: string[];
    typography_notes: string;
  };
  image_prompts: string[];  // For AI image generation
}

interface SlideSpec {
  slide_number: number;
  layout: string;           // e.g., "title_only", "text_with_image"
  headline: string;
  body_text: string | null;
  image_description: string | null;
  design_notes: string | null;
}
```

**Example**:
```json
{
  "visual_specs": {
    "total_slides": 8,
    "slides": [
      {
        "slide_number": 1,
        "layout": "title_only",
        "headline": "I Lost $50K on My First Startup",
        "body_text": null,
        "image_description": "Broken piggy bank or empty wallet",
        "design_notes": "Use red accent for impact"
      },
      {
        "slide_number": 2,
        "layout": "text_with_icon",
        "headline": "Here's What I Learned",
        "body_text": "3 lessons that changed everything",
        "image_description": "Lightbulb icon",
        "design_notes": "Transition slide, keep minimal"
      },
      ...
    ],
    "overall_style": "Clean, minimalist with bold typography",
    "color_palette": ["#1a1a2e", "#16213e", "#e94560", "#ffffff"],
    "typography_notes": "Use Impact or Montserrat Bold for headlines, Light weight for body"
  },
  "image_prompts": [
    "Minimalist illustration of broken piggy bank, dark background",
    "Abstract lightbulb made of connected dots, blue tones"
  ]
}
```

---

### 5.5 Optimizer Agent Output

```typescript
interface OptimizerOutput {
  decision: "APPROVE" | "REVISE";
  quality_score: number;              // 0-10
  brand_consistency_score: number;    // 0-10
  formatting_issues: string[];
  suggestions: string[];
  predicted_impressions_min: number;
  predicted_impressions_max: number;
  predicted_engagement_rate: number;  // 0-1 (e.g., 0.045 = 4.5%)
  confidence: number;                 // 0-1
}
```

**Example**:
```json
{
  "decision": "APPROVE",
  "quality_score": 8.5,
  "brand_consistency_score": 8.0,
  "formatting_issues": [],
  "suggestions": [
    "Consider adding a specific metric or result from your second startup",
    "The third lesson could be more specific - what exactly did you learn about resilience?",
    "Adding a personal photo in the comments often increases engagement by 20%"
  ],
  "predicted_impressions_min": 5000,
  "predicted_impressions_max": 15000,
  "predicted_engagement_rate": 0.045,
  "confidence": 0.72
}
```

---

### 5.6 Final Post Structure

```typescript
interface FinalPost {
  format: "text" | "carousel" | "video";
  hook: HookVariation;                    // Best hook selected
  body: string;                           // Full body content
  cta: string;                            // Call to action
  hashtags: string[];                     // List of hashtags (without #)
  visual_specs: VisualSpecs | null;       // Only for carousel
  quality_score: number;                  // 0-10
  predicted_impressions: [number, number]; // [min, max]
}
```

**Example**:
```json
{
  "format": "text",
  "hook": {
    "version": 1,
    "text": "I lost $50,000 and 18 months of my life.",
    "hook_type": "personal_story",
    "score": 9.0,
    "reasoning": "Leads with specific numbers and emotional vulnerability"
  },
  "body": "Here's what I learned building (and failing) a B2B SaaS for restaurants:\n\n1️⃣ Validate before you build\n...",
  "cta": "What's the biggest lesson failure has taught you?",
  "hashtags": ["startup", "entrepreneurship", "failure", "founder", "lessons"],
  "visual_specs": null,
  "quality_score": 8.5,
  "predicted_impressions": [5000, 15000]
}
```

---

## 6. State Machine

### 6.1 Generation States

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ POST /generate
                           ▼
                    ┌─────────────┐
                    │ PROCESSING  │◀──────────────┐
                    └──────┬──────┘               │
                           │                      │
              ┌────────────┼────────────┐         │
              ▼            ▼            ▼         │
       ┌──────────┐ ┌────────────┐ ┌────────┐    │
       │ REJECTED │ │ AWAITING   │ │ FAILED │    │
       │          │ │ ANSWERS    │ │        │    │
       └──────────┘ └─────┬──────┘ └────────┘    │
                          │                       │
                          │ POST /answers         │
                          ▼                       │
                   ┌─────────────┐                │
                   │ PROCESSING  │────────────────┘
                   └──────┬──────┘   (if REVISE)
                          │
                          ▼
                   ┌─────────────┐
                   │ COMPLETED   │
                   └─────────────┘
```

### 6.2 Agent States

Each agent can be in one of these states:
- `pending` - Not yet started
- `active` - Currently executing
- `success` - Completed successfully
- `error` - Failed (may retry)
- `skipped` - Not applicable (e.g., Visual for text posts)

---

## 7. Error Handling

### 7.1 Error Response Format

```json
{
  "error": "string - error type",
  "detail": "string - human readable message",
  "error_code": "string - machine readable code"
}
```

### 7.2 Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `IDEA_TOO_SHORT` | 400 | Idea less than 10 characters |
| `IDEA_TOO_LONG` | 400 | Idea more than 5000 characters |
| `POST_NOT_FOUND` | 404 | Post ID doesn't exist |
| `POST_EXPIRED` | 404 | Post ID expired from memory |
| `IDEA_REJECTED` | 422 | Validator rejected the idea |
| `LLM_ERROR` | 500 | AI model returned error |
| `RATE_LIMIT` | 429 | Too many requests |

### 7.3 Retry Behavior

- Each agent retries up to 3 times on failure
- Delay between retries: 1s, 2s, 3s (exponential backoff)
- If all retries fail, stream emits `agent_error` event and stops

---

## 8. Timing Expectations

### 8.1 Typical Execution Times

| Agent | Typical Time | Range |
|-------|--------------|-------|
| Validator | 1-2s | 0.5-4s |
| Strategist | 1-3s | 0.5-5s |
| Writer | 3-6s | 2-10s |
| Visual | 2-4s | 1-6s |
| Optimizer | 1-3s | 0.5-5s |
| **Total (text)** | **7-15s** | 5-25s |
| **Total (carousel)** | **10-20s** | 7-30s |

### 8.2 Progress Milestones

| Milestone | Progress % | Time (approx) |
|-----------|------------|---------------|
| Start | 0% | 0s |
| Validator complete | 15% | 1.5s |
| Strategist complete (Phase 1 done) | 30% | 3s |
| User answers submitted | 35% | user dependent |
| Writer complete | 55% | 8s |
| Visual complete (if carousel) | 75% | 11s |
| Optimizer complete | 90% | 13s |
| Finalized | 100% | 14s |

---

## 9. Complete Example Flow

### 9.1 Timeline of a Successful Generation

```
T+0.0s   User submits: "3 lessons I learned from failing my first startup"
T+0.0s   → POST /api/v1/posts/generate/stream
T+0.0s   ← SSE: agent_start (validator, 5%)
T+1.2s   ← SSE: agent_complete (validator, APPROVE, 8.5/10, 15%)
T+1.2s   ← SSE: agent_start (strategist, 20%)
T+2.8s   ← SSE: agent_complete (strategist, 4 questions, 30%)
T+2.8s   ← SSE: complete (awaiting_answers, questions)

[User answers questions - time varies]

T+X.0s   User submits answers
T+X.0s   → POST /api/v1/posts/{id}/answers/stream
T+X.0s   ← SSE: status_update ("Starting content generation", 35%)
T+X.0s   ← SSE: agent_start (writer, 45%)
T+X+4.2s ← SSE: agent_complete (writer, 3 hooks, body, 55%)
T+X+4.2s ← SSE: agent_start (optimizer, 80%)
T+X+6.1s ← SSE: agent_complete (optimizer, APPROVE, 8.5/10, 90%)
T+X+6.2s ← SSE: complete (completed, final_post, 100%)
```

---

## 10. Frontend Implementation Checklist

### What to Display at Each Stage:

**Stage: Input**
- [ ] Text area for idea (with character count)
- [ ] Format selector (optional)
- [ ] Submit button

**Stage: Processing (Phase 1)**
- [ ] Progress bar (0-30%)
- [ ] Agent timeline showing Validator → Strategist
- [ ] For each agent: name, status, time, score, thoughts

**Stage: Awaiting Answers**
- [ ] List of questions from strategist
- [ ] Each question shows: text, rationale, required flag
- [ ] Text input for each answer
- [ ] Progress indicator (X of Y answered)
- [ ] Submit button

**Stage: Processing (Phase 2)**
- [ ] Progress bar (35-100%)
- [ ] Agent timeline showing Writer → Visual → Optimizer
- [ ] Revision indicator if optimizer says REVISE

**Stage: Complete**
- [ ] Final post preview (hook + body + cta + hashtags)
- [ ] Hook selector (3 variations)
- [ ] Quality score display
- [ ] Predicted impressions range
- [ ] Predicted engagement rate
- [ ] Suggestions list from optimizer
- [ ] Copy button
- [ ] Save/export options

**Stage: Rejected**
- [ ] Rejection reason
- [ ] Quality score
- [ ] Suggestions for improvement
- [ ] Try again button

---

## 11. History API - Revisit Past Generations

The History API allows users to view any past generation, even after closing the browser.
All data is persisted in the PostgreSQL database.

### 11.1 List All Generation Histories

**Endpoint**: `GET /api/v1/history/`

**Query Parameters**:
- `limit` (int, default 20): Max items to return
- `offset` (int, default 0): Pagination offset

**Response**:
```json
{
  "histories": [
    {
      "history_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "post_id": "550e8400-e29b-41d4-a716-446655440000",
      "raw_idea": "3 lessons I learned from failing my first startup...",
      "status": "completed",
      "format": "text",
      "quality_score": 8.5,
      "total_execution_time_ms": 8542,
      "started_at": "2026-01-01T14:30:00.000Z",
      "completed_at": "2026-01-01T14:30:15.000Z"
    },
    ...
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

### 11.2 Get Complete Generation History

**Endpoint**: `GET /api/v1/history/{history_id}`

**Response** (Full history with all agent outputs):
```json
{
  "history_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  
  "raw_idea": "3 lessons I learned from failing my first startup",
  "preferred_format": "auto",
  "brand_profile_snapshot": {},
  
  "validator_output": {
    "decision": "APPROVE",
    "quality_score": 8.5,
    "brand_alignment_score": 7.0,
    "reasoning": "...",
    "concerns": ["..."],
    "refinement_suggestions": ["..."]
  },
  
  "strategist_output": {
    "recommended_format": "text",
    "format_reasoning": "...",
    "structure_type": "story_post",
    "hook_types": ["personal_story", "vulnerability"],
    "psychological_triggers": ["curiosity_gap", "relatability"],
    "clarifying_questions": [...]
  },
  
  "writer_output": {
    "hooks": [...],
    "body_content": "...",
    "cta": "...",
    "hashtags": [...]
  },
  
  "visual_output": {},
  
  "optimizer_output": {
    "decision": "APPROVE",
    "quality_score": 8.5,
    "predicted_impressions_min": 5000,
    "predicted_impressions_max": 15000,
    "predicted_engagement_rate": 0.045,
    "suggestions": [...]
  },
  
  "clarifying_questions": [
    {
      "question_id": "q1",
      "question": "What was the specific financial outcome?",
      "rationale": "Adds credibility",
      "required": true
    }
  ],
  
  "user_answers": {
    "q1": "We lost $50,000 and shut down after 18 months",
    "q2": "B2B SaaS for restaurants"
  },
  
  "final_post": {
    "format": "text",
    "hook": {...},
    "body": "...",
    "cta": "...",
    "hashtags": [...],
    "quality_score": 8.5,
    "predicted_impressions": [5000, 15000]
  },
  
  "selected_hook_index": 0,
  
  "status": "completed",
  "total_execution_time_ms": 8542,
  "revision_count": 0,
  
  "validator_time_ms": 1234,
  "strategist_time_ms": 856,
  "writer_time_ms": 4521,
  "visual_time_ms": null,
  "optimizer_time_ms": 1931,
  
  "error_message": null,
  "failed_agent": null,
  
  "started_at": "2026-01-01T14:30:00.000Z",
  "phase1_completed_at": "2026-01-01T14:30:02.500Z",
  "answers_submitted_at": "2026-01-01T14:31:00.000Z",
  "completed_at": "2026-01-01T14:31:08.542Z",
  
  "events": [
    {
      "event_id": "...",
      "event_type": "agent_start",
      "agent_name": "validator",
      "message": "🔄 Validator agent is analyzing...",
      "execution_time_ms": 0,
      "progress_percent": 5,
      "output_summary": null,
      "decision": null,
      "score": null,
      "timestamp": "2026-01-01T14:30:00.000Z"
    },
    {
      "event_id": "...",
      "event_type": "agent_complete",
      "agent_name": "validator",
      "message": "✅ Validator completed in 1234ms",
      "execution_time_ms": 1234,
      "progress_percent": 15,
      "output_summary": "Decision: APPROVE | Quality Score: 8.5/10",
      "decision": "APPROVE",
      "score": 8.5,
      "timestamp": "2026-01-01T14:30:01.234Z"
    },
    ...
  ],
  
  "agents_summary": [
    {
      "agent_name": "validator",
      "status": "success",
      "execution_time_ms": 1234,
      "decision": "APPROVE",
      "score": 8.5,
      "summary": "Decision: APPROVE | Quality: 8.5/10",
      "has_output": true
    },
    ...
  ]
}
```

---

### 11.3 Get History by Post ID

**Endpoint**: `GET /api/v1/history/post/{post_id}`

Same response as 11.2. Useful when you have the post_id but not history_id.

---

### 11.4 Get Timeline Events Only

**Endpoint**: `GET /api/v1/history/{history_id}/events`

**Response**:
```json
{
  "history_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "events": [
    {
      "event_id": "...",
      "event_type": "agent_start",
      "agent_name": "validator",
      "message": "🔄 Validator agent is analyzing...",
      "execution_time_ms": 0,
      "progress_percent": 5,
      "timestamp": "2026-01-01T14:30:00.000Z"
    },
    ...
  ],
  "total_events": 10
}
```

---

### 11.5 Get Specific Agent Output

**Endpoint**: `GET /api/v1/history/{history_id}/agent/{agent_name}`

**Valid agent_name values**: `validator`, `strategist`, `writer`, `visual`, `optimizer`

**Response**:
```json
{
  "history_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agent_name": "validator",
  "execution_time_ms": 1234,
  "has_output": true,
  "output": {
    "decision": "APPROVE",
    "quality_score": 8.5,
    ...
  },
  "summary": "Decision: APPROVE | Quality Score: 8.5/10 | Brand Alignment: 7.0/10"
}
```

---

### 11.6 Update Selected Hook

**Endpoint**: `PATCH /api/v1/history/{history_id}/selected-hook`

**Query Parameter**: `hook_index` (0, 1, or 2)

**Response**:
```json
{
  "history_id": "...",
  "selected_hook_index": 1,
  "status": "updated"
}
```

---

## 12. Database Schema for History

### Table: generation_history
Stores the complete generation flow for each post.

| Column | Type | Description |
|--------|------|-------------|
| history_id | UUID | Primary key |
| post_id | UUID | Foreign key to posts |
| user_id | UUID | Foreign key to users (optional) |
| raw_idea | TEXT | Original idea input |
| preferred_format | VARCHAR(50) | User's format preference |
| brand_profile_snapshot | JSONB | Copy of brand profile at generation time |
| validator_output | JSONB | Complete validator output |
| strategist_output | JSONB | Complete strategist output |
| writer_output | JSONB | Complete writer output |
| visual_output | JSONB | Complete visual output (if carousel) |
| optimizer_output | JSONB | Complete optimizer output |
| clarifying_questions | JSONB | Questions from strategist |
| user_answers | JSONB | User's answers to questions |
| final_post | JSONB | Final compiled post |
| selected_hook_index | INT | Which hook user selected (0-2) |
| status | VARCHAR(50) | pending/processing/awaiting_answers/completed/failed/rejected |
| total_execution_time_ms | INT | Total time from start to finish |
| revision_count | INT | Number of revision iterations |
| validator_time_ms | INT | Time for validator |
| strategist_time_ms | INT | Time for strategist |
| writer_time_ms | INT | Time for writer |
| visual_time_ms | INT | Time for visual |
| optimizer_time_ms | INT | Time for optimizer |
| error_message | TEXT | Error if failed |
| failed_agent | VARCHAR(100) | Which agent failed |
| started_at | TIMESTAMP | When generation started |
| phase1_completed_at | TIMESTAMP | When Phase 1 finished |
| answers_submitted_at | TIMESTAMP | When user submitted answers |
| completed_at | TIMESTAMP | When generation completed |

### Table: generation_events
Stores individual events for timeline view.

| Column | Type | Description |
|--------|------|-------------|
| event_id | UUID | Primary key |
| history_id | UUID | Foreign key to generation_history |
| event_type | VARCHAR(50) | agent_start/agent_complete/agent_error/status_update/complete |
| agent_name | VARCHAR(100) | validator/strategist/writer/visual/optimizer/system |
| message | TEXT | Human-readable message |
| execution_time_ms | INT | Time this agent took |
| progress_percent | INT | Overall progress 0-100 |
| output_summary | TEXT | Brief summary of output |
| decision | VARCHAR(50) | Agent decision (APPROVE/REJECT/REVISE) |
| score | FLOAT | Quality score |
| event_data | JSONB | Full event data |
| error_message | TEXT | Error message if failed |
| retry_attempt | INT | Retry attempt number |
| timestamp | TIMESTAMP | When event occurred |

---

This document contains all data structures and flows needed to build the UI.

