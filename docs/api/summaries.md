# Summaries API

## Overview

The Summaries API is the core feature of Saaransh Backend, providing AI-powered document summarization with collaborative editing capabilities. The API supports a two-stage workflow: **staging summaries** for initial AI generation and **final summaries** for refined, production-ready content.

## Summary Lifecycle

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Data     │    │  Staging        │    │  Final          │
│   (Tasks, Logs, │───▶│  Summary        │───▶│  Summary        │
│   Comments)     │    │  (AI Generated) │    │  (Refined)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Edit via LLM   │    │  Manual Save    │
                       │  (AI Assisted)  │    │  (Direct Edit)  │
                       └─────────────────┘    └─────────────────┘
```

## Summary Status Flow

```
STAGING ──────▶ IN_PROGRESS ──────▶ SUBMITTED
   │                 │                  │
   │                 ▼                  ▼
   │           SAVED_FOR_LATER    ARCHIVED
   │                 │
   ▼                 ▼
STAGED_FOR_SUBMIT ──┘
```

### Status Definitions

| Status | Value | Description |
|--------|-------|-------------|
| `STAGING` | 0 | Initial AI-generated summary for review |
| `IN_PROGRESS` | 1 | Summary being actively edited |
| `SUBMITTED` | 2 | Final summary ready for use |
| `ARCHIVED` | 3 | Historical versions maintained |
| `SAVED_FOR_LATER` | 4 | Drafts saved for future work |
| `STAGED_FOR_SUBMIT` | 5 | Ready for final submission |

## API Endpoints

### 1. Create Staging Summary

Generate an initial AI-powered summary from user task data.

**Endpoint:** `POST /api/v1/summaries/staging`

**Request Body:**
```json
{
  "model": "gemini/gemini-2.5-flash",
  "user_prompt": "Focus on technical achievements and challenges",
  "user_data": {
    "employee": {
      "name": "John Doe",
      "role": "Senior Software Engineer"
    },
    "tasks": [
      {
        "title": "API Development",
        "description": "Developed REST API for user management",
        "comments": [
          {
            "text": "Implemented OAuth2 authentication"
          }
        ],
        "logs": [
          {
            "content": "Completed endpoint testing with 95% coverage"
          }
        ]
      }
    ]
  }
}
```

**Response:**
```json
{
  "summary_sk": 12345,
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "<p>I successfully developed a comprehensive REST API for user management...</p>",
  "status_id": 0,
  "meta_data": {
    "model": "gemini/gemini-2.5-flash"
  },
  "is_active": true,
  "created_date": "2024-01-15T10:30:00Z",
  "created_by": "user-uuid",
  "effective_from": "2024-01-15T10:30:00Z",
  "effective_to": null
}
```

**Process Flow:**
1. **Data Processing**: User task data is formatted and chunked
2. **AI Generation**: LLM generates initial summary using staging prompt
3. **Embedding Creation**: Content embeddings are generated concurrently
4. **Database Storage**: Summary and embeddings are stored
5. **Permission Setup**: Creator is assigned OWNER role

### 2. Create Final Summary

Convert a staging summary to a final, refined version.

**Endpoint:** `POST /api/v1/summaries/final`

**Request Body:**
```json
{
  "model": "gemini/gemini-2.5-flash",
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "summary_sk": 12345,
  "user_prompt": "Make it more professional and add quantified results"
}
```

**Response:**
```json
{
  "summary_sk": 12346,
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "<p>I successfully architected and delivered a comprehensive REST API...</p>",
  "status_id": 1,
  "meta_data": {
    "model": "gemini/gemini-2.5-flash"
  },
  "is_active": true,
  "created_date": "2024-01-15T10:30:00Z",
  "created_by": "user-uuid",
  "effective_from": "2024-01-15T11:00:00Z",
  "effective_to": null
}
```

### 3. Fetch Summaries

Retrieve summaries with filtering and sorting options.

**Endpoint:** `GET /api/v1/summaries`

**Query Parameters:**
- `summary_id` (UUID, optional): Filter by specific summary ID
- `summary_sk` (int, optional): Filter by specific summary surrogate key
- `status_id` (int, optional): Filter by status
- `is_active` (bool, optional): Filter by active status
- `effective_only` (bool, optional): Show only current versions (default: true)
- `sort` (string, optional): Sort specification (e.g., "-created_date")

**Examples:**

```bash
# Get all active summaries, sorted by creation date (newest first)
GET /api/v1/summaries?sort=-created_date

# Get specific summary with all versions
GET /api/v1/summaries?summary_id=123e4567-e89b-12d3-a456-426614174000&effective_only=false

# Get summaries by status
GET /api/v1/summaries?status_id=2&sort=created_date
```

**Response:**
```json
[
  {
    "summary_sk": 12346,
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "<p>I successfully architected and delivered...</p>",
    "status_id": 1,
    "meta_data": {
      "model": "gemini/gemini-2.5-flash"
    },
    "is_active": true,
    "created_date": "2024-01-15T10:30:00Z",
    "created_by": "user-uuid",
    "effective_from": "2024-01-15T11:00:00Z",
    "effective_to": null
  }
]
```

### 4. Edit Summary via LLM

Use AI to edit an existing summary based on user instructions.

**Endpoint:** `PUT /api/v1/summaries/edit`

**Request Body:**
```json
{
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "summary_sk": 12346,
  "content": "<p>Current summary content...</p>",
  "user_prompt": "Add more details about the technical challenges faced",
  "staging": false
}
```

**Response:**
```json
{
  "summary_sk": 12347,
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "<p>I successfully architected and delivered a comprehensive REST API, overcoming significant technical challenges...</p>",
  "status_id": 1,
  "meta_data": {
    "model": "gemini/gemini-2.5-flash"
  },
  "is_active": true,
  "created_date": "2024-01-15T10:30:00Z",
  "created_by": "user-uuid",
  "modified_by": "user-uuid",
  "effective_from": "2024-01-15T11:30:00Z",
  "effective_to": null
}
```

**Features:**
- **Tool Integration**: Can query knowledge base for additional context
- **Version Control**: Creates new version while preserving history
- **Prompt Tracking**: User prompts are logged for audit trail
- **Staging Support**: Different prompts for staging vs final summaries

### 5. Save Modified Summary

Manually save changes to a summary without AI assistance.

**Endpoint:** `PUT /api/v1/summaries/save`

**Request Body:**
```json
{
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "summary_sk": 12347,
  "content": "<p>Manually edited summary content...</p>"
}
```

**Response:**
```json
{
  "summary_sk": 12348,
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "<p>Manually edited summary content...</p>",
  "status_id": 1,
  "is_active": true,
  "created_date": "2024-01-15T10:30:00Z",
  "created_by": "user-uuid",
  "modified_by": "user-uuid",
  "effective_from": "2024-01-15T12:00:00Z",
  "effective_to": null
}
```

## Data Models

### UserData Structure

The input data structure for summary generation:

```json
{
  "employee": {
    "name": "string",
    "role": "string"
  },
  "tasks": [
    {
      "title": "string",
      "description": "string",
      "comments": [
        {
          "text": "string"
        }
      ],
      "logs": [
        {
          "content": "string"
        }
      ]
    }
  ]
}
```

### Summary Response Model

```json
{
  "summary_sk": "integer",
  "summary_id": "uuid",
  "content": "string (HTML)",
  "start_date": "datetime (optional)",
  "end_date": "datetime (optional)",
  "status_id": "integer",
  "meta_data": "object",
  "is_active": "boolean",
  "created_date": "datetime",
  "created_by": "uuid",
  "modified_by": "uuid (optional)",
  "effective_from": "datetime",
  "effective_to": "datetime (optional)",
  "entity_type_id": "integer"
}
```

## AI Integration

### LLM Models

Supported models (configurable via environment):
- `gemini/gemini-2.5-flash` (default)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- Other LiteLLM-supported providers

### Prompt Templates

#### Staging Summary Prompt
```
You are an expert analyst generating intermediate summaries.

Given the employee profile and a list of tasks with descriptions, comments, and logs:

1. Produce a clear and comprehensive overview of each task.
2. Separate each task overview with a clear divider.
3. Capture important details:
   - Task purpose or goal
   - Key actions taken
   - Important comments or notes
   - Issues, blockers, or delays
   - Final outcomes or current status

These overviews will be used for final summary generation.
```

#### Final Summary Prompt
```
You are an assistant generating a professional year-end self-assessment report.
Write in first person using "I", "my", etc.

Structure:
1. Overview of Work
2. Key Accomplishments
3. Challenges and Resolutions
4. Skills Developed

Output should be WYSIWYG editor HTML (e.g., TipTap format).
```

#### Edit Prompts
- **Edit Prompt**: For final summaries - focused editing
- **Edit Staging Prompt**: For staging summaries - includes RAG tool calling

### Content Processing

#### Data Chunking
User task data is processed into chunks for optimal AI processing:

```python
def chunk_task_data(user_data: UserData) -> List[str]:
    chunks = []
    for i, task in enumerate(user_data.tasks, 1):
        # Main task chunk
        chunks.append(f"Task {i} - {task.title} Description: {task.description}")
        
        # Comments chunk (if exists)
        if task.comments:
            comments_text = f"Task {i} - {task.title}\nComments:\n" + \
                          "\n".join([f"- {comment.text}" for comment in task.comments])
            chunks.append(comments_text)
        
        # Logs chunk (if exists)
        if task.logs:
            logs_text = f"Task {i} - {task.title}\nActivity Logs:\n" + \
                       "\n".join([f"- {log.content}" for log in task.logs])
            chunks.append(logs_text)
    
    return chunks
```

#### Embedding Generation
Content embeddings are generated for semantic search:

```python
# Concurrent processing during staging summary creation
llm_future = self.llm_accessor.get_response(model, prompt, user_prompt, system_prompt)
embedding_future = self.embedding_builder.process_and_store_embeddings(
    summary_id=summary_id, 
    content=request.user_data, 
    session=self.session
)

llm_text, _ = await asyncio.gather(llm_future, embedding_future)
```

## Version Control (SCD2)

### Slowly Changing Dimensions Type 2

All summaries use SCD2 for complete version history:

- **Active Record**: `effective_to = NULL`
- **Historical Records**: `effective_to = timestamp`
- **Version Chain**: Same `summary_id`, different `summary_sk`

### Version Management

```python
# Close current version
await self.summary_accessor.close_active_record(summary_id, session)

# Create new version
new_summary = Summary(
    summary_id=summary_id,  # Same ID
    content=new_content,
    effective_from=datetime.now(timezone.utc),
    effective_to=None,      # New active version
    created_by=original_creator,
    modified_by=current_user
)
```

## Error Handling

### Common Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `Invalid request data` | Malformed request body |
| 401 | `Authentication required` | Missing or invalid token |
| 404 | `Summary not found` | Summary ID doesn't exist |
| 422 | `Validation error` | Invalid field values |
| 500 | `LLM service error` | AI service unavailable |
| 503 | `Service unavailable` | External service failure |

### Error Response Format

```json
{
  "detail": "Summary not found for summary_id=123e4567-e89b-12d3-a456-426614174000",
  "type": "not_found"
}
```

## Usage Examples

### Complete Workflow Example

```python
import httpx
import asyncio

async def complete_summary_workflow():
    headers = {"Authorization": "Bearer your-jwt-token"}
    base_url = "https://api.saaransh.com/api/v1/summaries"
    
    # 1. Create staging summary
    staging_request = {
        "user_prompt": "Focus on technical achievements",
        "user_data": {
            "employee": {"name": "John Doe", "role": "Engineer"},
            "tasks": [
                {
                    "title": "API Development",
                    "description": "Built REST API",
                    "comments": [{"text": "Added OAuth2"}],
                    "logs": [{"content": "95% test coverage"}]
                }
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Create staging
        staging_response = await client.post(
            f"{base_url}/staging",
            json=staging_request,
            headers=headers
        )
        staging_summary = staging_response.json()
        summary_id = staging_summary["summary_id"]
        
        # Edit via LLM
        edit_request = {
            "summary_id": summary_id,
            "user_prompt": "Add more quantified results",
            "staging": True
        }
        
        edit_response = await client.put(
            f"{base_url}/edit",
            json=edit_request,
            headers=headers
        )
        
        # Create final summary
        final_request = {
            "summary_id": summary_id,
            "user_prompt": "Make it professional for HR submission"
        }
        
        final_response = await client.post(
            f"{base_url}/final",
            json=final_request,
            headers=headers
        )
        
        return final_response.json()
```

### Filtering and Sorting Examples

```bash
# Get all summaries for a user, newest first
curl -X GET "https://api.saaransh.com/api/v1/summaries?sort=-created_date" \
  -H "Authorization: Bearer your-token"

# Get submitted summaries only
curl -X GET "https://api.saaransh.com/api/v1/summaries?status_id=2" \
  -H "Authorization: Bearer your-token"

# Get all versions of a specific summary
curl -X GET "https://api.saaransh.com/api/v1/summaries?summary_id=123e4567-e89b-12d3-a456-426614174000&effective_only=false" \
  -H "Authorization: Bearer your-token"
```

## Performance Considerations

### Concurrent Processing
- **Parallel Operations**: LLM generation and embedding creation run concurrently
- **Async Architecture**: Non-blocking operations throughout
- **Connection Pooling**: Efficient database connection management

### Caching Strategy
- **JWKS Caching**: Authentication keys cached with LRU
- **Model Singleton**: Embedding model loaded once at startup
- **Token Caching**: M2M tokens cached with automatic refresh

### Optimization Tips
- Use appropriate chunk sizes for large task datasets
- Implement request timeouts for LLM calls
- Monitor token usage and costs
- Consider summary length limits for performance

## Security Considerations

### Access Control
- All endpoints require authentication
- Summary ownership tracked via `created_by`
- Role-based permissions for sharing (see Summaries Users API)

### Data Privacy
- User task data processed securely
- No persistent storage of raw task data
- Audit trail maintained for all changes

### Input Validation
- Comprehensive request validation
- HTML sanitization for content
- Size limits on input data