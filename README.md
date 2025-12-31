# LinkedIn AI Agent System

🚀 **A production-grade, multi-agent AI system for generating high-performing LinkedIn posts**

> Powered by Google Gemini API

---

## ✨ Features

- **5 Specialized AI Agents**: Each optimized for a specific task
  - 🔍 **Validator**: Quality gates and brand alignment
  - 📊 **Strategist**: Format selection and clarifying questions
  - ✍️ **Writer**: Hook and content generation
  - 🎨 **Visual**: Carousel and image specifications
  - ⚡ **Optimizer**: Quality assurance and performance prediction

- **RAG System**: Reference successful posts for pattern matching
- **Brand Consistency**: Maintain your unique voice across posts
- **Performance Prediction**: Estimate engagement before posting

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd linkedin-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: GEMINI_API_KEY
```

### 3. Run the CLI

```bash
python -m src.cli.main
```

### 4. Or Start the API

```bash
uvicorn src.api.main:app --reload
```

---

## 📁 Project Structure

```
linkedin-ai-agent/
├── src/
│   ├── agents/           # AI agents (Validator, Strategist, etc.)
│   ├── orchestration/    # LangGraph workflow
│   ├── rag/              # Vector store and retrieval
│   ├── llm/              # Gemini API client
│   ├── models/           # Pydantic data models
│   ├── database/         # PostgreSQL repositories
│   ├── api/              # FastAPI endpoints
│   └── cli/              # Command-line interface
├── tests/                # Unit, integration, and E2E tests
├── data/                 # Reference posts (gitignored)
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

---

## 🔧 Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google AI Studio API key | ✅ Yes |
| `DATABASE_URL` | PostgreSQL connection | For persistence |
| `REDIS_URL` | Redis connection | For caching |
| `CHROMADB_PATH` | Local vector store path | Development |

---

## 📊 Agent Pipeline

```
Raw Idea 
   → Validator (quality check)
   → Strategist (format + questions)
   → [User answers]
   → Writer (content generation)
   → [Visual (if carousel)]
   → Optimizer (QA + prediction)
   → Final Post
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src

# Run specific test category
pytest tests/unit/ -v
```

---

## 📈 Cost Estimates

| Per Generation | Cost |
|----------------|------|
| Gemini API | ~$0.15-0.30 |
| **Total** | **~$0.30/post** |

| Monthly Infrastructure | Cost |
|------------------------|------|
| Free tier start | $0 |
| With persistence | ~$50-100 |

---

## 📖 Documentation

- [Implementation Plan](./docs/implementation_plan.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Progress Tracking](./PROGRESS.md)

---

## 🤝 Contributing

1. Check [PROGRESS.md](./PROGRESS.md) for current status
2. Review open issues
3. Create a feature branch
4. Submit a pull request

---

## 📝 License

MIT License

---

*Built with ❤️ using Google Gemini AI*
