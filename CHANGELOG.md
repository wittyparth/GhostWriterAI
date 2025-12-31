# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-31

### Added

#### Core Features
- 🤖 **Multi-Agent System** - 5 specialized AI agents (Validator, Strategist, Writer, Visual, Optimizer)
- 🔄 **LangGraph Orchestration** - Intelligent workflow with conditional routing
- 💡 **Swappable Models** - Support for Gemini 3 Flash and Gemini 3 Pro
- 📚 **RAG System** - ChromaDB vector store with similarity search
- 💰 **Cost Tracking** - Token usage and cost estimation

#### API & CLI
- 🌐 **FastAPI REST API** - Full-featured API with OpenAPI docs
- 📝 **Interactive CLI** - Rich-based terminal interface
- 🔐 **Rate Limiting** - Built-in protection (30 req/min)
- ❤️ **Health Checks** - Basic and detailed health endpoints

#### Database & Storage
- 🗄️ **PostgreSQL Support** - Async SQLAlchemy with connection pooling
- 📦 **Alembic Migrations** - Database schema management
- 💾 **Redis Caching** - Session state and caching

#### DevOps
- 🐳 **Docker Support** - Dockerfile and docker-compose
- 🚀 **CI/CD** - GitHub Actions for testing and deployment
- 🧪 **Test Suite** - Unit, integration, and E2E tests

### Technical Details
- Python 3.11+ required
- Async-first architecture
- Type hints throughout
- Comprehensive logging

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2025-12-31 | Initial release |

[Unreleased]: https://github.com/yourusername/linkedin-ai-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/linkedin-ai-agent/releases/tag/v0.1.0
