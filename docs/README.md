# Saaransh Backend - Complete System Documentation

## Overview

**Saaransh Backend** is a sophisticated FastAPI-based web service that provides AI-powered document summarization with collaborative features. The system enables users to create, edit, and collaborate on AI-generated summaries while maintaining version control and role-based access permissions.

### Core Purpose

Saaransh (Sanskrit for "summary" or "essence") serves as an intelligent document processing platform that:

- **Generates AI-powered summaries** using multiple LLM providers (Gemini, OpenAI, etc.)
- **Enables collaborative editing** with comments, sharing, and role-based permissions
- **Provides semantic search** through vector embeddings and pgvector integration
- **Integrates with external systems** like Asana and Nirdesh for workflow automation
- **Maintains data integrity** through versioning and audit trails

### Key Features

1. **AI-Powered Summarization**
   - Multi-provider LLM integration via LiteLLM
   - Staging and final summary workflows
   - Interactive summary editing with natural language prompts

2. **Collaborative Platform**
   - Role-based access control (Owner, Editor, Viewer, Admin)
   - Real-time commenting system
   - Summary sharing and permission management

3. **Advanced Search & Analytics**
   - Vector embeddings for semantic similarity
   - Content-based search capabilities
   - User interaction tracking and analytics

4. **Enterprise Integration**
   - Keycloak OAuth2/OIDC authentication
   - Asana project management integration
   - Nirdesh external system connectivity

## System Architecture

### Layered Architecture Pattern

Saaransh follows a clean, layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Handlers)                     │
│  FastAPI routers, request validation, response formatting   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Business Logic (Builders)                   │
│   Complex operations, business rules, workflow orchestration │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Data Access (Accessors)                      │
│  Database operations, external APIs, data transformation    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Data Layer (Models & Database)                 │
│     PostgreSQL, SQLAlchemy ORM, Pydantic validation        │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

The typical request flow follows this pattern:

1. **Handler** receives HTTP request and validates input
2. **Builder** orchestrates business logic and coordinates operations
3. **Accessor** performs database operations or external API calls
4. **Model** provides data validation and transformation
5. Response flows back through the same layers

## Project Structure

```
saaransh_backend/
├── app/                          # Main application package
│   ├── handlers/                 # API endpoints (Controllers)
│   │   ├── summaries_handler.py  # Summary CRUD operations
│   │   ├── comments_handler.py   # Comment management
│   │   ├── users_handler.py      # User management
│   │   └── ...                   # Other API handlers
│   │
│   ├── builders/                 # Business logic layer
│   │   ├── summaries_builder.py  # Summary business operations
│   │   ├── comments_builder.py   # Comment business logic
│   │   └── ...                   # Other business services
│   │
│   ├── accessors/                # Data access layer
│   │   ├── summaries_accessor.py # Summary database operations
│   │   ├── llm/                  # LLM service integration
│   │   ├── integrations/         # External service connectors
│   │   └── ...                   # Other data access classes
│   │
│   ├── models/                   # Data models and schemas
│   │   ├── orm/                  # SQLAlchemy database models
│   │   ├── request/              # API request schemas
│   │   ├── response/             # API response schemas
│   │   └── constants.py          # System constants and enums
│   │
│   ├── config/                   # Configuration and setup
│   │   ├── database.py           # Database configuration
│   │   ├── logging.py            # Logging setup
│   │   └── security/             # Authentication & authorization
│   │
│   ├── components/               # Shared components
│   │   └── embeddings_model.py   # Singleton embedding model
│   │
│   ├── tools/                    # Utility tools
│   │   ├── query_knowledge_base.py # Knowledge base queries
│   │   └── registry.py           # Tool registry
│   │
│   ├── utils/                    # Helper utilities
│   │   ├── scd2_protocol.py      # Data versioning utilities
│   │   ├── sort_util.py          # Sorting and pagination
│   │   └── ...                   # Other utilities
│   │
│   ├── main.py                   # FastAPI application setup
│   └── settings.py               # Environment configuration
│
├── docs/                         # Documentation (this directory)
├── .env.example                  # Environment variables template
├── pyproject.toml               # Project dependencies and metadata
├── serve.py                     # Application entry point
├── Justfile                     # Task automation (Just)
└── Taskfile.yml                 # Task automation (Task)
```

## Core Design Patterns

### 1. Repository Pattern
- **Implementation**: Accessor classes abstract database operations
- **Benefits**: Loose coupling between business logic and data access
- **Example**: `SummariesAccessor` handles all summary-related database operations

### 2. Builder Pattern
- **Implementation**: Builder classes orchestrate complex business operations
- **Benefits**: Encapsulates complex object construction and business rules
- **Example**: `SummaryBuilder` manages the entire summary creation workflow

### 3. Dependency Injection
- **Implementation**: FastAPI's dependency system for loose coupling
- **Benefits**: Testable, maintainable, and configurable components
- **Example**: Database sessions and authentication injected into handlers

### 4. Factory Pattern
- **Implementation**: LLM service creation based on configuration
- **Benefits**: Runtime provider selection and easy extensibility
- **Example**: `LLMFactory` creates appropriate LLM service instances

### 5. Singleton Pattern
- **Implementation**: Embedding model management for resource efficiency
- **Benefits**: Single model instance shared across requests
- **Example**: `EmbeddingModelSingleton` loads model once at startup

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Uvicorn**: ASGI server for high-performance async applications
- **Python 3.12**: Latest Python version with enhanced performance

### Database & ORM
- **PostgreSQL**: Robust relational database with advanced features
- **SQLAlchemy 2.0**: Modern ORM with async support
- **pgvector**: PostgreSQL extension for vector similarity search
- **asyncpg**: High-performance async PostgreSQL driver

### AI & Machine Learning
- **LiteLLM**: Universal interface for multiple LLM providers
- **Sentence Transformers**: Pre-trained models for text embeddings
- **Supported LLM Providers**: Gemini, OpenAI, and others

### Authentication & Security
- **Keycloak**: Enterprise-grade identity and access management
- **OAuth2/OIDC**: Standard authentication protocols
- **JWT**: Secure token-based authentication
- **Authlib**: Comprehensive OAuth library

### Development & Deployment
- **uv**: Fast Python package manager and dependency resolver
- **Just/Task**: Command runners for development automation
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management

## Key Concepts

### Summary Lifecycle
1. **Staging**: Initial AI-generated summary for review
2. **In Progress**: Summary being actively edited
3. **Submitted**: Final summary ready for use
4. **Archived**: Historical versions maintained
5. **Saved for Later**: Drafts saved for future work

### Role-Based Access Control
- **Owner**: Full control over summary and permissions
- **Editor**: Can modify content and add comments
- **Viewer**: Read-only access to summaries
- **Admin**: System-wide administrative privileges

### Data Versioning (SCD2)
- **Slowly Changing Dimensions**: Track historical changes
- **Audit Trail**: Complete history of modifications
- **Point-in-Time Recovery**: Access any previous version

### Vector Embeddings
- **Semantic Search**: Find similar content based on meaning
- **Content Similarity**: Compare documents beyond keyword matching
- **Recommendation Engine**: Suggest related summaries

## Getting Started

### Quick Start
1. **Install Dependencies**: `uv sync`
2. **Configure Environment**: Copy `.env.example` to `.env`
3. **Start Server**: `just start` or `task start`
4. **Access API**: Visit `http://localhost:8000/docs`

### Prerequisites
- Python 3.12+
- PostgreSQL with pgvector extension
- Keycloak server (for authentication)
- LLM API keys (Gemini, OpenAI, etc.)

## Documentation Structure

This documentation is organized into the following sections:

- **[Architecture](architecture/)** - Detailed system design and component relationships
- **[API Reference](api/)** - Complete endpoint documentation with examples
- **[Development Guide](development/)** - Code organization and contribution guidelines
- **[Deployment](deployment/)** - Production deployment and configuration
- **[Features](features/)** - Business functionality and user workflows
- **[Troubleshooting](troubleshooting/)** - Common issues and solutions

## Next Steps

- **For Developers**: Start with the [Development Guide](development/) and [API Reference](api/)
- **For System Administrators**: Review [Architecture](architecture/) and [Deployment](deployment/)
- **For Business Users**: Explore [Features](features/) and user workflows
- **For Troubleshooting**: Check [Common Issues](troubleshooting/) and debugging guides