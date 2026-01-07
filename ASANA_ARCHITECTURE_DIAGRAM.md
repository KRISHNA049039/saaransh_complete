# Asana Integration Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Frontend Apps  │  Mobile Apps  │  CLI Tools  │  External Integrations     │
└─────────────────┴───────────────┴─────────────┴─────────────────────────────┘
                                    │
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                    asana_integration_controllers.py                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   /status   │ │ /overview   │ │/workspace/  │ │     /task/{gid}     │   │
│  │             │ │             │ │   {gid}     │ │                     │   │
│  │ Health      │ │ Complete    │ │ Workspace   │ │ Task Details &      │   │
│  │ Check       │ │ User Data   │ │ Specific    │ │ Stories             │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Function Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                      asana_nirdesh_pipeline.py                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    get_asana_accessor()                             │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │   │
│  │  │ Check ENABLE_   │    │ Import Asana    │    │ Return Accessor │ │   │
│  │  │ ASANA env var   │───▶│ Accessor Class  │───▶│ or None         │ │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Object Creation
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                           asana_accessor.py                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AsanaAccessor Class                            │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │   │
│  │  │ get_current_    │  │ get_workspaces  │  │ get_projects        │ │   │
│  │  │ user()          │  │ ()              │  │ (workspace_gid)     │ │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │   │
│  │  │ get_tasks_for_  │  │ get_task_       │  │ get_user_data_for_  │ │   │
│  │  │ user()          │  │ stories()       │  │ report()            │ │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL API                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                      Asana REST API                                         │
│                   https://app.asana.com/api/1.0                             │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   /users/   │ │/workspaces  │ │ /projects   │ │      /tasks         │   │
│  │     me      │ │             │ │             │ │                     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              REQUEST FLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. Client Request
   │
   ▼
2. FastAPI Controller
   │ ┌─────────────────────────────────────────────────────────────────────┐
   │ │ • Route validation                                                  │
   │ │ • Request parsing                                                   │
   │ │ • Authentication check                                              │
   │ └─────────────────────────────────────────────────────────────────────┘
   ▼
3. Pipeline Factory
   │ ┌─────────────────────────────────────────────────────────────────────┐
   │ │ • Check ENABLE_ASANA environment variable                           │
   │ │ • Create AsanaAccessor instance if enabled                          │
   │ │ • Return None if disabled (graceful degradation)                    │
   │ └─────────────────────────────────────────────────────────────────────┘
   ▼
4. Service Layer
   │ ┌─────────────────────────────────────────────────────────────────────┐
   │ │ • Validate access token                                             │
   │ │ • Create HTTP session                                               │
   │ │ • Execute business logic                                            │
   │ │ • Handle API responses                                              │
   │ └─────────────────────────────────────────────────────────────────────┘
   ▼
5. Asana API Calls
   │ ┌─────────────────────────────────────────────────────────────────────┐
   │ │ • Bearer token authentication                                       │
   │ │ • RESTful HTTP requests                                             │
   │ │ • JSON response parsing                                             │
   │ │ • Rate limit handling                                               │
   │ └─────────────────────────────────────────────────────────────────────┘
   ▼
6. Response Processing
   │ ┌─────────────────────────────────────────────────────────────────────┐
   │ │ • Data aggregation and enrichment                                   │
   │ │ • Error handling and logging                                        │
   │ │ • Response formatting                                               │
   │ │ • HTTP status code setting                                          │
   │ └─────────────────────────────────────────────────────────────────────┘
   ▼
7. Client Response
```

## GID Hierarchy Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ASANA GID HIERARCHY                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   User GID      │
                              │ 1212000333310446│ ◄─── Authentication Root
                              └─────────────────┘
                                       │
                                       │ get_workspaces()
                                       ▼
                              ┌─────────────────┐
                              │ Workspace GID   │
                              │ 1205513962325788│ ◄─── User's Accessible Workspaces
                              └─────────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        │              │              │
                        ▼              ▼              ▼
              ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
              │  Project GID    │ │   Task GID      │ │   Team GID      │
              │ 1212000280291519│ │ 1212000280291534│ │      ...        │
              └─────────────────┘ └─────────────────┘ └─────────────────┘
                       │                   │
                       │                   │ get_task_stories()
                       ▼                   ▼
              ┌─────────────────┐ ┌─────────────────┐
              │   Subtasks      │ │   Story GID     │
              │      ...        │ │ 1212000336269036│
              └─────────────────┘ └─────────────────┘

API Call Patterns:
├── get_current_user() ────────────────────────► User GID
├── get_workspaces() ──────────────────────────► Workspace GIDs
├── get_projects(workspace_gid) ───────────────► Project GIDs
├── get_tasks_for_user(user_gid, workspace_gid) ► Task GIDs
└── get_task_stories(task_gid) ────────────────► Story GIDs
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT INTERACTIONS                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Controllers   │    │    Pipeline     │    │    Accessor     │
│                 │    │                 │    │                 │
│ • /status       │───▶│ get_asana_      │───▶│ AsanaAccessor   │
│ • /overview     │    │ accessor()      │    │ __init__()      │
│ • /workspace    │    │                 │    │                 │
│ • /task         │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
└─────────────────┘    │ │Environment  │ │    │ │HTTP Session │ │
         │              │ │Validation   │ │    │ │Setup        │ │
         │              │ └─────────────┘ │    │ └─────────────┘ │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Response      │    │   Error         │    │   Asana API     │
│   Formatting    │    │   Handling      │    │   Calls         │
│                 │    │                 │    │                 │
│ • JSON          │◄───│ • Logging       │◄───│ • REST          │
│ • Status Codes  │    │ • Graceful      │    │ • Bearer Auth   │
│ • Validation    │    │   Degradation   │    │ • Rate Limits   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Error Flow:
API Error ──► Accessor Logging ──► Pipeline Handling ──► Controller Response

Success Flow:
API Data ──► Accessor Processing ──► Pipeline Return ──► Controller Format
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT VIEW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Production Environment:
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Load Balancer                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                   │                                         │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
│    │   App Server 1  │    │   App Server 2  │    │   App Server N  │       │
│    │                 │    │                 │    │                 │       │
│    │ FastAPI         │    │ FastAPI         │    │ FastAPI         │       │
│    │ Asana Module    │    │ Asana Module    │    │ Asana Module    │       │
│    │ Environment:    │    │ Environment:    │    │ Environment:    │       │
│    │ ENABLE_ASANA=   │    │ ENABLE_ASANA=   │    │ ENABLE_ASANA=   │       │
│    │ true            │    │ true            │    │ true            │       │
│    └─────────────────┘    └─────────────────┘    └─────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTPS/TLS
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Asana Cloud                                    │
│                         https://app.asana.com                               │
│                                                                             │
│  Rate Limiting: 150 requests/minute per token                              │
│  Authentication: Bearer Token                                               │
│  Data: Workspaces, Projects, Tasks, Stories                                │
└─────────────────────────────────────────────────────────────────────────────┘

Configuration Management:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │     Staging     │    │   Production    │
│                 │    │                 │    │                 │
│ .env file       │    │ Environment     │    │ Secret Manager  │
│ Local tokens    │    │ Variables       │    │ Encrypted       │
│ Debug logging   │    │ Test tokens     │    │ Audit logging   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SECURITY LAYERS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. Network Security
   ┌─────────────────────────────────────────────────────────────────────┐
   │ • HTTPS/TLS encryption for all API calls                           │
   │ • Firewall rules for outbound Asana API access                     │
   │ • VPN/Private network for internal communications                   │
   └─────────────────────────────────────────────────────────────────────┘

2. Authentication Security
   ┌─────────────────────────────────────────────────────────────────────┐
   │ • Personal Access Tokens (PAT) from Asana                          │
   │ • Bearer token authentication                                       │
   │ • Token validation on each request                                  │
   │ • Graceful handling of expired/invalid tokens                      │
   └─────────────────────────────────────────────────────────────────────┘

3. Application Security
   ┌─────────────────────────────────────────────────────────────────────┐
   │ • Environment variable isolation                                    │
   │ • No hardcoded credentials                                          │
   │ • Input validation and sanitization                                 │
   │ • Error message sanitization (no token exposure)                    │
   └─────────────────────────────────────────────────────────────────────┘

4. Data Security
   ┌─────────────────────────────────────────────────────────────────────┐
   │ • No persistent storage of Asana tokens                            │
   │ • Minimal data retention (API responses only)                      │
   │ • Audit logging for all API calls                                  │
   │ • Rate limit compliance                                             │
   └─────────────────────────────────────────────────────────────────────┘

Token Flow Security:
Environment → Pipeline → Accessor → HTTP Headers → Asana API
     ↑            ↑          ↑           ↑            ↑
 Encrypted    Validation  Session    Bearer      TLS/HTTPS
 Storage      Check       Reuse      Auth        Encryption
```

---

*These diagrams provide a visual representation of the Asana integration architecture and can be used for documentation, onboarding, and system design discussions.*