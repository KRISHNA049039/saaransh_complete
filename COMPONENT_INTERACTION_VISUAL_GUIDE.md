# Component Interaction Visual Guide

## System Component Map

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                CLIENT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  API Client  │  Postman/Curl  │  Third Party    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                   HTTP/HTTPS
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│              AWS ALB / Nginx / CloudFlare (SSL Termination)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                 Round Robin
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI APPLICATION                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        MIDDLEWARE STACK                                 │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │ CORS │ Auth │ Logging │ Rate Limit │ Request ID │ Error Handler        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         ROUTER LAYER                                    │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                         │   │
│  │  /api/v1/asana/*     /api/v1/llm/*      /health/*                      │   │
│  │  ┌─────────────┐     ┌─────────────┐    ┌─────────────┐                │   │
│  │  │AsanaRouter  │     │ LLMRouter   │    │HealthRouter │                │   │
│  │  │             │     │             │    │             │                │   │
│  │  │ - workspaces│     │ - chat      │    │ - liveness  │                │   │
│  │  │ - projects  │     │ - summarize │    │ - readiness │                │   │
│  │  │ - tasks     │     │ - debug     │    │ - metrics   │                │   │
│  │  │ - stories   │     │             │    │             │                │   │
│  │  └─────────────┘     └─────────────┘    └─────────────┘                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        HANDLER LAYER                                    │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │CommentsHdlr │  │ TaskHandler │  │ LLMHandler  │  │ProjectHdlr  │    │   │
│  │  │             │  │             │  │             │  │             │    │   │
│  │  │ - validate  │  │ - create    │  │ - generate  │  │ - list      │    │   │
│  │  │ - enhance   │  │ - update    │  │ - summarize │  │ - details   │    │   │
│  │  │ - create    │  │ - delete    │  │ - chat      │  │ - tasks     │    │   │
│  │  │ - list      │  │ - assign    │  │             │  │             │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       ACCESSOR LAYER                                    │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                         │   │
│  │  ┌─────────────┐              ┌─────────────────────────────────────┐   │   │
│  │  │AsanaAccessor│              │           LLM FACTORY               │   │   │
│  │  │             │              ├─────────────────────────────────────┤   │   │
│  │  │ - auth      │              │                                     │   │   │
│  │  │ - rate_limit│              │  ┌─────────────┐ ┌─────────────┐    │   │   │
│  │  │ - transform │              │  │OpenAIAccess │ │LocalLlama   │    │   │   │
│  │  │ - retry     │              │  │             │ │Accessor     │    │   │   │
│  │  │ - cache     │              │  │ - gpt-3.5   │ │             │    │   │   │
│  │  └─────────────┘              │  │ - gpt-4     │ │ - llama3.1  │    │   │   │
│  │                               │  │ - embeddings│ │ - ollama    │    │   │   │
│  │                               │  └─────────────┘ └─────────────┘    │   │   │
│  │                               └─────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                              External API Calls
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Asana API   │    │ Ollama      │    │ OpenAI API  │    │ Redis Cache │      │
│  │             │    │ Server      │    │             │    │             │      │
│  │ - REST API  │    │             │    │ - Chat API  │    │ - Session   │      │
│  │ - OAuth     │    │ - Llama3.1  │    │ - Embeddings│    │ - Cache     │      │
│  │ - Webhooks  │    │ - Local GPU │    │ - Fine-tune │    │ - Pub/Sub   │      │
│  │ - Rate Limit│    │ - CPU/RAM   │    │ - Moderation│    │             │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Patterns

### 1. Synchronous Request Flow (Standard API Call)

```
Client Request
      │
      ▼
┌─────────────┐
│Load Balancer│ ──── SSL Termination, Health Check
└─────────────┘
      │
      ▼
┌─────────────┐
│ Middleware  │ ──── CORS, Auth, Logging, Rate Limiting
│   Stack     │
└─────────────┘
      │
      ▼
┌─────────────┐
│   Router    │ ──── Route Matching, Parameter Extraction
│             │
└─────────────┘
      │
      ▼
┌─────────────┐
│   Handler   │ ──── Business Logic, Validation
│             │
└─────────────┘
      │
      ▼
┌─────────────┐
│  Accessor   │ ──── External API Calls, Data Transform
│             │
└─────────────┘
      │
      ▼
┌─────────────┐
│ External    │ ──── Asana API, LLM Services
│ Service     │
└─────────────┘
      │
      ▼
Response Chain (reverse order)
```

### 2. AI-Enhanced Request Flow (With LLM Processing)

```
Client Request (with AI enhancement)
      │
      ▼
┌─────────────┐
│   Handler   │ ──── Validate Request
└─────────────┘
      │
      ▼
┌─────────────┐
│Asana Check  │ ──── Verify Task/Project Exists
└─────────────┘
      │
      ▼
┌─────────────┐
│LLM Factory  │ ──── Select AI Provider (Local/Remote)
└─────────────┘
      │
      ▼
┌─────────────┐
│AI Processing│ ──── Generate/Enhance Content
└─────────────┘
      │
      ▼
┌─────────────┐
│Asana Update │ ──── Create/Update with Enhanced Content
└─────────────┘
      │
      ▼
┌─────────────┐
│   Response  │ ──── Return Enhanced Result
└─────────────┘
```

### 3. Error Handling Flow

```
Exception Occurs
      │
      ▼
┌─────────────┐
│Exception    │ ──── Catch at Handler Level
│Handler      │
└─────────────┘
      │
      ▼
┌─────────────┐
│Error        │ ──── Classify Error Type
│Classification│
└─────────────┘
      │
      ├── Validation Error (400)
      ├── Auth Error (401)
      ├── Not Found (404)
      ├── External API Error (502/503)
      └── Internal Error (500)
      │
      ▼
┌─────────────┐
│Error        │ ──── Log, Transform, Respond
│Response     │
└─────────────┘
      │
      ▼
┌─────────────┐
│Client Gets  │ ──── Structured Error Response
│Error        │
└─────────────┘
```

## Component Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEPENDENCY FLOW                          │
└─────────────────────────────────────────────────────────────────┘

main.py (Application Root)
    │
    ├── settings.py (Configuration)
    │
    ├── routers/
    │   ├── asana_router.py
    │   │   └── depends on: handlers/
    │   ├── llm_router.py
    │   │   └── depends on: handlers/
    │   └── health_router.py
    │       └── depends on: accessors/
    │
    ├── handlers/ (Business Logic)
    │   ├── comments_handler.py
    │   │   ├── depends on: accessors/asana_accessor.py
    │   │   ├── depends on: accessors/llm/llm_factory.py
    │   │   └── depends on: models/
    │   ├── task_handler.py
    │   │   ├── depends on: accessors/asana_accessor.py
    │   │   └── depends on: models/
    │   └── llm_handler.py
    │       ├── depends on: accessors/llm/llm_factory.py
    │       └── depends on: models/
    │
    ├── accessors/ (Data Access)
    │   ├── asana_accessor.py
    │   │   ├── depends on: httpx (external)
    │   │   └── depends on: settings.py
    │   └── llm/
    │       ├── llm_factory.py
    │       │   ├── depends on: llm_accessor.py (interface)
    │       │   ├── depends on: openai_accessor.py
    │       │   ├── depends on: local_llama_accessor.py
    │       │   └── depends on: settings.py
    │       ├── llm_accessor.py (Abstract Base)
    │       ├── openai_accessor.py
    │       │   ├── depends on: openai (external)
    │       │   └── depends on: llm_accessor.py
    │       └── local_llama_accessor.py
    │           ├── depends on: httpx (external)
    │           └── depends on: llm_accessor.py
    │
    └── models/ (Data Models)
        ├── request_models.py
        ├── response_models.py
        └── asana_models.py

External Dependencies:
├── fastapi (Web Framework)
├── pydantic (Data Validation)
├── httpx (HTTP Client)
├── openai (OpenAI SDK)
├── uvicorn (ASGI Server)
└── python-dotenv (Environment Variables)
```

## Interaction Sequence Diagrams

### 1. Task Comment Creation with AI Enhancement

```
User    Router    Handler    AsanaAccessor    LLMFactory    LocalLLM    AsanaAPI
 │        │         │            │              │            │           │
 │ POST   │         │            │              │            │           │
 ├───────▶│         │            │              │            │           │
 │        │ create  │            │              │            │           │
 │        ├────────▶│            │              │            │           │
 │        │         │ validate   │              │            │           │
 │        │         ├──────────┐ │              │            │           │
 │        │         │◀─────────┘ │              │            │           │
 │        │         │ get_task   │              │            │           │
 │        │         ├───────────▶│              │            │           │
 │        │         │            │ GET /tasks   │            │           │
 │        │         │            ├─────────────────────────────────────▶│
 │        │         │            │              │            │  task     │
 │        │         │ task_data  │◀─────────────────────────────────────┤
 │        │         │◀───────────┤              │            │           │
 │        │         │ enhance_ai │              │            │           │
 │        │         ├──────────┐ │              │            │           │
 │        │         │ get_llm  │ │              │            │           │
 │        │         ├───────────────────────────▶│            │           │
 │        │         │          │ │ create_local │            │           │
 │        │         │          │ ├─────────────▶│            │           │
 │        │         │ llm_acc  │ │              │ llm_inst   │           │
 │        │         │◀───────────────────────────┤◀───────────┤           │
 │        │         │ generate │ │              │            │           │
 │        │         ├─────────────────────────────────────────▶│           │
 │        │         │          │ │              │ /generate  │           │
 │        │         │          │ │              │ ├─────────▶│           │
 │        │         │          │ │              │ │response  │           │
 │        │         │ enhanced │ │              │ │◀─────────┤           │
 │        │         │◀─────────────────────────────────────────┤           │
 │        │         │◀─────────┘ │              │            │           │
 │        │         │create_story│              │            │           │
 │        │         ├───────────▶│              │            │           │
 │        │         │            │POST /stories │            │           │
 │        │         │            ├─────────────────────────────────────▶│
 │        │         │            │              │            │  story    │
 │        │         │ story_data │◀─────────────────────────────────────┤
 │        │         │◀───────────┤              │            │           │
 │        │response │            │              │            │           │
 │        │◀────────┤            │              │            │           │
 │ 201    │         │            │              │            │           │
 │◀───────┤         │            │              │            │           │
```

### 2. LLM Factory Pattern Execution

```
Handler    LLMFactory    Settings    LocalLlamaAccessor    OllamaService
   │           │            │               │                    │
   │get_llm()  │            │               │                    │
   ├──────────▶│            │               │                    │
   │           │get_config()│               │                    │
   │           ├───────────▶│               │                    │
   │           │config_data │               │                    │
   │           │◀───────────┤               │                    │
   │           │create()    │               │                    │
   │           ├──────────────────────────▶│                    │
   │           │            │ __init__()    │                    │
   │           │            │ ├───────────┐ │                    │
   │           │            │ │setup_client│                    │
   │           │            │ ├───────────▶│                    │
   │           │            │ │           │ │ /api/tags          │
   │           │            │ │           │ ├───────────────────▶│
   │           │            │ │           │ │ models_list        │
   │           │            │ │ ready     │ │◀───────────────────┤
   │           │            │ │◀──────────┤ │                    │
   │           │            │ │◀──────────┘ │                    │
   │           │ accessor   │               │                    │
   │           │◀──────────────────────────┤               │    │
   │ llm_inst  │            │               │                    │
   │◀──────────┤            │               │                    │
```

### 3. Error Propagation Flow

```
Client    Router    Handler    Accessor    ExternalAPI    ErrorHandler
  │         │         │          │            │              │
  │ request │         │          │            │              │
  ├────────▶│         │          │            │              │
  │         │ call    │          │            │              │
  │         ├────────▶│          │            │              │
  │         │         │ api_call │            │              │
  │         │         ├─────────▶│            │              │
  │         │         │          │ HTTP req   │              │
  │         │         │          ├───────────▶│              │
  │         │         │          │            │ 500 Error    │
  │         │         │          │ Exception  │◀─────────────┤
  │         │         │ Exception│◀───────────┤              │
  │         │ Exception│◀─────────┤            │              │
  │         │◀────────┤          │            │              │
  │         │ handle  │          │            │              │
  │         ├─────────────────────────────────────────────────▶│
  │         │         │          │            │ log_error()   │
  │         │         │          │            │ ├───────────┐ │
  │         │         │          │            │ │classify() │ │
  │         │         │          │            │ ├───────────┤ │
  │         │         │          │            │ │format()   │ │
  │         │         │          │            │ │◀──────────┘ │
  │         │ error_response     │            │               │
  │         │◀─────────────────────────────────────────────────┤
  │ 502 Bad │         │          │            │              │
  │◀────────┤         │          │            │              │
```

## Performance Optimization Points

### 1. Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    CACHING LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Browser   │  │     CDN     │  │ Load Balancer│        │
│  │   Cache     │  │   Cache     │  │    Cache     │        │
│  │ (Static)    │  │ (Static)    │  │ (Headers)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │Application  │  │   Redis     │  │  Database   │         │
│  │   Cache     │  │   Cache     │  │   Cache     │         │
│  │ (Memory)    │  │ (Shared)    │  │ (Query)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘

Cache Hierarchy:
1. Browser Cache (Static assets) - 24 hours
2. CDN Cache (API responses) - 5 minutes
3. Application Memory Cache - 1 hour
4. Redis Shared Cache - 6 hours
5. Database Query Cache - 30 minutes
```

### 2. Connection Pooling

```
┌─────────────────────────────────────────────────────────────┐
│                 CONNECTION MANAGEMENT                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FastAPI Application                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Connection Pools                     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │ Asana Pool  │  │ Ollama Pool │  │ Redis Pool  │ │   │
│  │  │             │  │             │  │             │ │   │
│  │  │ Size: 20    │  │ Size: 5     │  │ Size: 10    │ │   │
│  │  │ Timeout: 30s│  │ Timeout: 60s│  │ Timeout: 5s │ │   │
│  │  │ Retry: 3    │  │ Retry: 2    │  │ Retry: 1    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Pool Configuration:
- Asana API: 20 connections, 30s timeout, 3 retries
- Ollama: 5 connections, 60s timeout, 2 retries  
- Redis: 10 connections, 5s timeout, 1 retry
```

### 3. Async Processing Pipeline

```
Request Processing Pipeline:

Synchronous Path (Fast Operations):
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Validate│→│ Cache   │→│ Simple  │→│Response │
│ Input   │ │ Check   │ │ Query   │ │ Return  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
   ~5ms       ~10ms       ~50ms       ~5ms

Asynchronous Path (Heavy Operations):
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Queue   │→│Background│→│ AI      │→│ Callback│
│ Task    │ │ Worker  │ │ Process │ │ Notify  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
   ~10ms      ~100ms      ~2000ms     ~50ms

Immediate Response: 202 Accepted + Task ID
Final Result: WebSocket/Webhook notification
```

This visual guide provides a comprehensive view of how all components interact within the Saaransh backend system, showing the clear separation of concerns and well-defined data flow patterns that make the system maintainable and scalable.