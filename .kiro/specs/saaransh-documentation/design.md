# Design Document

## Overview

This design outlines the creation of comprehensive documentation for the existing Saaransh Backend system. The documentation will analyze and explain the current codebase architecture, design patterns, data flow, and conceptual framework already implemented in the workspace.

Saaransh Backend is a FastAPI-based application that provides AI-powered document summarization with collaborative features. The system uses a layered architecture with clear separation of concerns, implementing patterns like Repository, Builder, and Dependency Injection. The documentation will reverse-engineer and explain these existing patterns and architectural decisions.

## Architecture

### Current System Analysis

The documentation will analyze and document the existing Saaransh Backend architecture, which follows these key patterns:

1. **Layered Architecture** - Clear separation between handlers, builders, accessors, and models
2. **Repository Pattern** - Data access abstraction through accessor classes
3. **Builder Pattern** - Complex object construction and business logic encapsulation
4. **Dependency Injection** - FastAPI's dependency system for loose coupling
5. **Factory Pattern** - LLM service creation and configuration
6. **Singleton Pattern** - Embedding model management

### System Components to Document

Based on the existing codebase structure:

```
app/
├── handlers/          # API endpoints and request handling
├── builders/          # Business logic and object construction
├── accessors/         # Data access and external service integration
├── models/           # Data models, requests, responses, ORM
├── config/           # Configuration, database, security setup
├── components/       # Shared components (embeddings, etc.)
├── tools/            # Utility tools and registries
└── utils/            # Helper functions and utilities
```

### Key Architectural Concepts

1. **Request Flow**: Handler → Builder → Accessor → Database/External Service
2. **Authentication**: Keycloak integration with JWT tokens
3. **AI Integration**: LiteLLM abstraction for multiple LLM providers
4. **Database**: PostgreSQL with SQLAlchemy ORM and pgvector for embeddings
5. **External Integrations**: Asana and Nirdesh service connections

## Components and Interfaces

### Core System Components Analysis

#### 1. Handler Layer (API Controllers)
- **Current Implementation**: FastAPI routers with dependency injection
- **Key Files**: `app/handlers/*.py`
- **Patterns**: RESTful API design, async/await, dependency injection
- **Responsibilities**: Request validation, response formatting, authentication enforcement

#### 2. Builder Layer (Business Logic)
- **Current Implementation**: Service classes that orchestrate business operations
- **Key Files**: `app/builders/*.py`
- **Patterns**: Builder pattern, composition over inheritance
- **Responsibilities**: Complex object construction, business rule enforcement, workflow orchestration

#### 3. Accessor Layer (Data Access)
- **Current Implementation**: Repository pattern with SQLAlchemy ORM
- **Key Files**: `app/accessors/*.py`
- **Patterns**: Repository pattern, async database operations
- **Responsibilities**: Database operations, external API calls, data transformation

#### 4. Model Layer (Data Structures)
- **Current Implementation**: Pydantic models for validation, SQLAlchemy for ORM
- **Key Files**: `app/models/`
- **Patterns**: Data Transfer Objects (DTOs), ORM mapping
- **Responsibilities**: Data validation, serialization, database schema definition

#### 5. Configuration Layer
- **Current Implementation**: Environment-based configuration with defaults
- **Key Files**: `app/config/`, `app/settings.py`
- **Patterns**: Configuration object pattern, dependency injection
- **Responsibilities**: Environment management, security setup, database configuration

### Integration Interfaces

#### 1. LLM Integration
- **Implementation**: LiteLLM factory pattern for multiple providers
- **Location**: `app/accessors/llm/`
- **Supported Providers**: Gemini, OpenAI (configurable)
- **Pattern**: Factory + Strategy pattern

#### 2. Authentication System
- **Implementation**: Keycloak OAuth2/OIDC integration
- **Location**: `app/config/security/`
- **Pattern**: Middleware pattern with JWT validation

#### 3. External Service Integration
- **Implementation**: Asana and Nirdesh API connectors
- **Location**: `app/accessors/integrations/`
- **Pattern**: Adapter pattern for external APIs

## Data Models

### Current Data Model Analysis

#### 1. Core Business Entities
Based on the existing codebase, the system manages these key entities:

- **Summaries**: AI-generated document summaries with versioning
- **Comments**: Collaborative feedback on summaries
- **Users**: User accounts with role-based permissions
- **User Prompts**: History of user interactions with AI
- **Content Embeddings**: Vector representations for semantic search

#### 2. Status and Role Management
- **Summary Status**: STAGING, IN_PROGRESS, SUBMITTED, ARCHIVED, SAVED_FOR_LATER, STAGED_FOR_SUBMIT
- **User Roles**: OWNER, EDITOR, VIEWER, ADMIN
- **Permission Model**: Role-based access control with summary-level permissions

#### 3. Data Flow Patterns
- **SCD2 Protocol**: Slowly Changing Dimensions for data versioning
- **Request/Response DTOs**: Separate models for API contracts
- **ORM Entities**: Database-mapped models with relationships

### Integration Data Models

#### 1. External Service Models
- **Asana Integration**: Task and project data synchronization
- **Nirdesh Integration**: External system data exchange
- **Keycloak Models**: User authentication and authorization data

#### 2. AI/ML Data Structures
- **Embedding Vectors**: High-dimensional vectors for semantic similarity
- **LLM Requests/Responses**: Structured data for AI service communication
- **Prompt Templates**: Reusable AI interaction patterns

## Error Handling

### Current Error Handling Patterns

#### 1. API Error Handling
- **FastAPI Exception Handling**: HTTP status codes and error responses
- **Validation Errors**: Pydantic model validation with detailed error messages
- **Authentication Errors**: JWT validation and Keycloak integration errors

#### 2. Database Error Handling
- **SQLAlchemy Exceptions**: Database connection and query error management
- **Transaction Management**: Async session handling and rollback strategies
- **Connection Pooling**: Database connection lifecycle management

#### 3. External Service Error Handling
- **LLM Service Errors**: Timeout, rate limiting, and API failure handling
- **Integration Failures**: Asana and Nirdesh service unavailability
- **Network Resilience**: Retry mechanisms and circuit breaker patterns

### Logging and Monitoring

#### Current Implementation
- **Structured Logging**: Configurable log levels and formatting
- **Request Tracing**: HTTP request/response logging
- **Error Tracking**: Exception logging with context information

## Testing Strategy

### Documentation Content Strategy

#### 1. Code Analysis and Documentation
- **Static Code Analysis**: Examine existing patterns and architectural decisions
- **Dependency Mapping**: Document component relationships and data flow
- **API Endpoint Analysis**: Catalog all available endpoints and their purposes
- **Configuration Analysis**: Document all environment variables and settings

#### 2. Architecture Documentation Approach
- **Reverse Engineering**: Analyze existing code to understand design patterns
- **Flow Diagrams**: Create visual representations of request/response flows
- **Component Interaction**: Document how different layers communicate
- **Design Pattern Identification**: Catalog and explain used patterns

#### 3. Conceptual Documentation
- **Business Logic Explanation**: Document the "why" behind architectural decisions
- **Use Case Analysis**: Explain how different features work together
- **Integration Points**: Document external service interactions
- **Data Lifecycle**: Explain how data flows through the system

### Documentation Validation

#### 1. Technical Accuracy
- **Code Review**: Verify documentation matches actual implementation
- **Example Validation**: Ensure code examples are current and functional
- **Architecture Verification**: Confirm diagrams reflect actual system structure

#### 2. Completeness Assessment
- **Component Coverage**: Ensure all major components are documented
- **Feature Documentation**: Cover all business functionality
- **Integration Documentation**: Document all external service connections
- **Configuration Coverage**: Document all setup and deployment aspects