# System Architecture

## Overview
The **LinkedIn AI Agent** (GhostWriterAI) is a sophisticated multi-agent system designed to generate high-quality LinkedIn content. It leverages Google Gemini for LLM capabilities, a RAG pipeline for context awareness, and a React-based frontend for user interaction.

## Architecture Diagram

```mermaid
graph TD
    %% Frontend
    subgraph Frontend [Frontend (React + Vite)]
        UI[User Interface]
        AuthStore[Auth Store]
        PostStore[Post Store]
        StreamService[Streaming Service]
    end

    %% Backend
    subgraph Backend [Backend (FastAPI)]
        API[API Gateway]
        
        subgraph Agents [Multi-Agent System]
            Strategist[Strategist Agent]
            Writer[Writer Agent]
            Optimizer[Optimizer Agent]
            Visual[Visual Agent]
            Validator[Validator Agent]
            Orchestrator[Orchestration Layer]
        end
        
        subgraph Services [Core Services]
            AuthService[Auth Service]
            EmailService[Email Service (Brevo)]
            BrandService[Brand Profile Service]
        end
        
        subgraph RAG [RAG Pipeline]
            Retriever[Retriever]
            Embeddings[Embeddings Service]
        end
    end

    %% Data Storage
    subgraph Data [Data Layer]
        Postgres[(PostgreSQL)]
        Chroma[(ChromaDB)]
        Redis[(Redis Cache)]
    end

    %% External
    subgraph External [External Services]
        Gemini[Google Gemini API]
        Brevo[Brevo Email API]
    end

    %% Connections
    UI --> API
    StreamService --> API
    
    API --> AuthService
    API --> BrandService
    API --> Orchestrator
    
    AuthService --> Postgres
    AuthService --> EmailService
    EmailService --> Brevo
    
    BrandService --> Postgres
    
    Orchestrator --> Strategist
    Orchestrator --> Writer
    Orchestrator --> Visual
    Orchestrator --> Optimizer
    Orchestrator --> Validator
    
    Strategist --> RAG
    Writer --> RAG
    
    RAG --> Retriever
    Retriever --> Chroma
    Retriever --> Embeddings
    Embeddings --> Gemini
    
    Strategist --> Gemini
    Writer --> Gemini
    Optimizer --> Gemini
    Validator --> Gemini
    Visual --> Gemini
    
    Orchestrator --> Redis
    
    %% Styles
    style Frontend fill:#e1f5fe,stroke:#01579b
    style Backend fill:#e8f5e9,stroke:#2e7d32
    style Agents fill:#fff3e0,stroke:#ef6c00
    style Data fill:#f3e5f5,stroke:#7b1fa2
    style External fill:#fce4ec,stroke:#c2185b
```

## Component Details

### 1. Frontend (Client)
- **Tech Stack**: React, Vite, TypeScript, TailwindCSS, Shadcn UI.
- **Responsibilities**:
  - User authentication and profile management.
  - Interactive chat/content generation interface.
  - Real-time streaming of agent activities.
  - Displaying generated posts and history.

### 2. Backend (Server)
- **Tech Stack**: Python, FastAPI, Uvicorn.
- **Key Modules**:
  - **API Routes**: `auth`, `brand_profile`, `posts`, `streaming`.
  - **Services**: Business logic for users, profiles, and external integrations.
  - **Security**: JWT-based authentication.

### 3. Multi-Agent System
Powered by **LangGraph** and **Google Gemini**:
- **Strategist Agent**: Analyzes trends and plans content strategy.
- **Writer Agent**: Drafts the actual post content based on the strategy.
- **Visual Agent**: Suggests or generates image prompts/assets.
- **Optimizer Agent**: Refines the content for SEO and engagement.
- **Validator Agent**: Ensures the content meets brand guidelines and safety checks.
- **Orchestrator**: Manages the state and flow between agents.

### 4. RAG Pipeline (Retrieval-Augmented Generation)
- **Tech Stack**: LangChain, ChromaDB.
- **Function**: Retrieves relevant past posts, brand guidelines, and successful patterns to inform the generation process.

### 5. Data Layer
- **PostgreSQL**: Primary database for users, brand profiles, and post history. Managed via SQLAlchemy and Alembic.
- **ChromaDB**: Vector database for storing embeddings of content and context.
- **Redis**: Used for caching and potentially task queues (if applicable).

### 6. External Integrations
- **Google Gemini**: The core LLM engine.
- **Brevo**: Service for sending transactional emails (e.g., verification).

## Data Flow (Content Generation)
1. User submits a topic or request via the **Frontend**.
2. **API** receives the request and initiates the **Orchestrator**.
3. **Strategist Agent** retrieves context via **RAG** and plans the post.
4. **Writer Agent** drafts the content using the plan.
5. **Visual Agent** adds image suggestions.
6. **Optimizer Agent** refines the draft.
7. **Validator Agent** gives final approval.
8. The final result is streamed back to the **Frontend** and saved to **PostgreSQL**.
