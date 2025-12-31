# API Documentation

## Overview

The LinkedIn AI Agent provides a REST API for programmatic access to post generation capabilities.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses rate limiting based on IP address. Future versions will support API key authentication.

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

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
    {"name": "database", "status": "healthy", "latency_ms": 5},
    {"name": "cache", "status": "healthy", "latency_ms": 2},
    {"name": "llm", "status": "healthy", "message": "Gemini API configured"}
  ]
}
```

---

### Generate Post

Start generating a post from an idea.

```http
POST /api/v1/posts/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "raw_idea": "3 lessons I learned from failing my startup",
  "user_id": "optional-user-id",
  "format_preference": "text"
}
```

**Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "questions": [
    {
      "question_id": "q1",
      "question": "What was the specific outcome of your startup?",
      "rationale": "Adds credibility with concrete results",
      "required": true
    },
    {
      "question_id": "q2", 
      "question": "Which lesson had the biggest impact on you?",
      "rationale": "Creates emotional connection",
      "required": false
    }
  ],
  "original_idea": "3 lessons I learned from failing my startup"
}
```

---

### Submit Answers

Submit answers to clarifying questions to complete generation.

```http
POST /api/v1/posts/{post_id}/answers
Content-Type: application/json
```

**Request Body:**
```json
{
  "answers": [
    {"question_id": "q1", "answer": "We ran out of funding after 18 months"},
    {"question_id": "q2", "answer": "The importance of product-market fit"}
  ]
}
```

**Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "post": {
    "format": "text",
    "hook": {
      "text": "I burned through $500K before learning this lesson.",
      "score": 8.7
    },
    "body": "After 18 months of building...",
    "cta": "What's the hardest lesson you've learned?",
    "hashtags": ["startup", "founder", "lessons"]
  },
  "quality_score": 8.5,
  "predicted_engagement": 0.045
}
```

---

### Get Post Status

Check the status of a post generation.

```http
GET /api/v1/posts/{post_id}/status
```

**Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "awaiting_answers",
  "current_agent": "strategist",
  "progress_percent": 50
}
```

**Possible Statuses:**
- `processing` - Generation in progress
- `awaiting_answers` - Waiting for user answers
- `completed` - Generation complete
- `failed` - Generation failed

---

### Get Post

Retrieve a completed post.

```http
GET /api/v1/posts/{post_id}
```

**Response:**
```json
{
  "post_id": "550e8400-e29b-41d4-a716-446655440000",
  "raw_idea": "3 lessons I learned from failing my startup",
  "final_content": "I burned through $500K...",
  "format": "text",
  "status": "completed",
  "quality_score": 8.5,
  "created_at": "2025-12-31T12:00:00Z"
}
```

---

### List Posts

List all generated posts.

```http
GET /api/v1/posts?limit=20&offset=0
```

**Response:**
```json
{
  "posts": [
    {
      "post_id": "550e8400-e29b-41d4-a716-446655440000",
      "raw_idea": "3 lessons I learned...",
      "format": "text",
      "status": "completed",
      "created_at": "2025-12-31T12:00:00Z"
    }
  ],
  "count": 1
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error (idea rejected) |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

### Rate Limiting

- **Limit:** 30 requests per minute per IP
- **Headers:**
  - `X-RateLimit-Limit`: Total allowed requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `Retry-After`: Seconds until reset (when limited)

---

## SDKs

### Python Example

```python
import httpx

async def generate_post(idea: str):
    async with httpx.AsyncClient() as client:
        # Start generation
        response = await client.post(
            "http://localhost:8000/api/v1/posts/generate",
            json={"raw_idea": idea}
        )
        data = response.json()
        
        # Answer questions
        answers = [{"question_id": q["question_id"], "answer": "..."} 
                   for q in data["questions"]]
        
        result = await client.post(
            f"http://localhost:8000/api/v1/posts/{data['post_id']}/answers",
            json={"answers": answers}
        )
        return result.json()
```

### JavaScript Example

```javascript
async function generatePost(idea) {
  // Start generation
  const response = await fetch('http://localhost:8000/api/v1/posts/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_idea: idea })
  });
  const data = await response.json();
  
  // Submit answers
  const result = await fetch(`http://localhost:8000/api/v1/posts/${data.post_id}/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers: [...] })
  });
  return result.json();
}
```

---

## Interactive Documentation

When the API is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
