# AI/LLM Integration Architecture

## Overview

Saaransh Backend implements a sophisticated AI integration architecture using LiteLLM as a universal interface to multiple Large Language Model providers. The system supports tool-assisted AI interactions, vector-based knowledge retrieval, and comprehensive prompt management for generating high-quality summaries and content editing.

## Architecture Components

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Handlers      │    │    Builders     │    │  LLM Factory    │
│   (API Layer)   │───▶│ (Business Logic)│───▶│   (Provider     │
│                 │    │                 │    │   Selection)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tool Registry │    │  Prompt Engine  │    │  LiteLLM        │
│   (RAG Tools)   │◀───│  (Templates)    │◀───│  Accessor       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                          ┌─────────────────┐
│Vector Knowledge │                          │   External      │
│Base (pgvector)  │                          │   LLM APIs      │
│                 │                          │ (Gemini, OpenAI)│
└─────────────────┘                          └─────────────────┘
```

### Key Features

1. **Multi-Provider Support**: Unified interface for multiple LLM providers
2. **Tool Integration**: RAG-enabled AI with knowledge base queries
3. **Prompt Management**: Structured prompt templates for different use cases
4. **Vector Search**: Semantic similarity search using embeddings
5. **Async Operations**: Non-blocking AI operations with proper error handling
6. **Token Management**: Token counting and cost optimization

## LiteLLM Integration

### Factory Pattern Implementation

```python
def get_llm_accessor(llm_sdk: Optional[str] = None) -> LLMAccessor:
    llm_sdk = settings.LLM_SDK.strip().lower() or "litellm"
    
    if llm_sdk == "litellm":
        return LiteLLMAccessor()
    else:
        raise ValueError(f"Unknown LLM sdk: {llm_sdk}")
```

**Benefits:**
- **Runtime Configuration**: Switch providers via environment variables
- **Easy Extension**: Add new providers without changing existing code
- **Testability**: Mock different providers for testing
- **Centralized Management**: Single point for provider configuration

### LLM Accessor Interface

```python
class LLMAccessor(ABC):
    @abstractmethod
    async def get_response(
        self,
        model: str,
        content: str,
        user_prompt: Optional[str],
        system_prompt: str,
        use_tools: bool = False,
        tool_schemas=None,
        tool_registry=None,
    ) -> str:
        """Generate LLM response with optional tool integration."""
        pass

    @abstractmethod
    async def get_token_count(self, text: str) -> int:
        """Calculate token count for cost estimation."""
        pass
```

**Interface Benefits:**
- **Abstraction**: Hide provider-specific implementation details
- **Consistency**: Uniform API across different providers
- **Flexibility**: Support for various AI interaction patterns
- **Tool Integration**: Built-in support for function calling

## LiteLLM Accessor Implementation

### Core Response Generation

```python
class LiteLLMAccessor:
    async def get_response(
        self,
        model: str,
        content: str,
        user_prompt: str,
        system_prompt: str,
        use_tools: bool = False,
        tool_schemas=None,
        tool_registry=None,
    ):
        try:
            logger.debug(f"--- Using model: {model} (tools={use_tools}) ---")
            
            # Build message structure
            messages = await self._build_messages(content, user_prompt, system_prompt)
            
            # Initial LLM request
            response = await acompletion(
                model=model,
                messages=messages,
                tools=tool_schemas if use_tools else None,
                tool_choice="auto" if use_tools else None,
            )
            
            response_message = response.choices[0].message
            
            # Handle tool calls if present
            if use_tools and response_message.tool_calls:
                tool_msgs = await self._run_tools(response_message, tool_registry)
                messages.append(response_message)
                messages.extend(tool_msgs)
                
                # Final response after tool execution
                final_response = await acompletion(model=model, messages=messages)
                return final_response.choices[0].message.content
            
            return response_message.content
            
        except Exception as e:
            logger.error(f"Error calling LiteLLM: {e}")
            raise
```

### Message Structure Building

```python
async def _build_messages(self, content: str, user_prompt: str, system_prompt: str):
    messages = []
    
    # System prompt for context and instructions
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Combine user instructions with content
    final_content = (
        f"user_instructions: {user_prompt}\n\n{content}" 
        if user_prompt else content
    )
    
    messages.append({"role": "user", "content": final_content})
    return messages
```

### Tool Execution Framework

```python
async def _run_tools(self, response_message, tool_registry):
    tool_calls = response_message.tool_calls or []
    if not tool_calls:
        return []
    
    logger.debug(f"--- LLM requested {len(tool_calls)} tool(s) ---")
    
    tasks = []
    call_ids = []
    
    # Prepare concurrent tool execution
    for call in tool_calls:
        fn_name = call.function.name
        args = json.loads(call.function.arguments)
        call_ids.append(call.id)
        
        logger.debug(f"Running tool: {fn_name} with args: {args}")
        
        if fn_name in tool_registry:
            fn = tool_registry[fn_name]
            tasks.append(fn(**args))
        else:
            tasks.append(
                asyncio.create_task(
                    asyncio.sleep(0, result=f"Error: Unknown tool '{fn_name}'")
                )
            )
    
    # Execute all tools concurrently
    results = await asyncio.gather(*tasks)
    
    # Format results for LLM
    return [
        {"role": "tool", "tool_call_id": call_ids[i], "content": results[i]}
        for i in range(len(results))
    ]
```

## Supported LLM Providers

### Configuration

```python
# Environment configuration
LLM_SDK = "litellm"  # Always use LiteLLM as interface
DEFAULT_LLM_MODEL = "gemini/gemini-2.5-flash"

# Supported models (via LiteLLM)
SUPPORTED_MODELS = [
    # Google Gemini
    "gemini/gemini-2.5-flash",
    "gemini/gemini-1.5-pro",
    "gemini/gemini-1.5-flash",
    
    # OpenAI
    "openai/gpt-4",
    "openai/gpt-4-turbo",
    "openai/gpt-3.5-turbo",
    
    # Anthropic Claude
    "anthropic/claude-3-opus",
    "anthropic/claude-3-sonnet",
    
    # Other providers supported by LiteLLM
    "cohere/command-r-plus",
    "mistral/mistral-large",
]
```

### Provider-Specific Features

| Provider | Models | Tool Support | Context Length | Strengths |
|----------|--------|--------------|----------------|-----------|
| **Google Gemini** | 2.5-flash, 1.5-pro | ✅ Function Calling | 1M+ tokens | Fast, cost-effective, large context |
| **OpenAI** | GPT-4, GPT-3.5 | ✅ Function Calling | 128K tokens | High quality, reliable |
| **Anthropic** | Claude-3 | ✅ Tool Use | 200K tokens | Excellent reasoning, safety |
| **Cohere** | Command-R+ | ✅ Tools | 128K tokens | Good for RAG applications |

## Tool Integration System

### Tool Registry

```python
TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {
    "query_knowledge_base": query_knowledge_base,
}

TOOL_DEFINITIONS = [
    tool_query_knowledge_base_definition
]
```

### Knowledge Base Query Tool

```python
async def query_knowledge_base(
    query: str,
    summary_id: UUID,
    top_k: int = 5,
) -> str:
    """Query vector knowledge base for relevant context."""
    
    async with SessionLocal() as session:
        try:
            # Generate query embedding
            query_vector = embedding_model.embed([query])[0]
            
            # Find similar content chunks
            results = await content_embedding_accessor.find_similar(
                session=session,
                embedding=query_vector,
                summary_id=summary_id,
                limit=top_k,
            )
            
            if not results:
                return "No relevant context found."
            
            # Format results for LLM
            formatted_chunks = [
                f"[Match {i}] (chunk {rec.chunk_index})\n{rec.content}"
                for i, rec in enumerate(results, start=1)
            ]
            
            return "\n\n".join(formatted_chunks)
            
        except Exception as e:
            logger.exception("Error querying knowledge base")
            return f"Error querying knowledge base: {e}"
```

### Tool Definition Schema

```python
tool_query_knowledge_base_definition = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": "Search the vector knowledge base for relevant context. minimum top_k is 3 and you can call this tool any number of times but only use it when you think rag is required for the user instruction",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
}
```

### Tool Wrapper Pattern

```python
def make_query_knowledge_base_wrapper(summary_id: UUID):
    """Create a tool wrapper with bound summary_id."""
    async def wrapper(query: str, top_k: int = 5):
        return await query_knowledge_base(
            query=query,
            summary_id=summary_id,
            top_k=top_k,
        )
    return wrapper

# Usage in summary builder
tool_schemas, tool_registry = self.build_tools(summary_id)
response = await self.llm_accessor.get_response(
    model=model_name,
    content=summary,
    user_prompt=user_query,
    system_prompt=system_prompt,
    use_tools=True,
    tool_schemas=tool_schemas,
    tool_registry=tool_registry,
)
```

## Prompt Management System

### Prompt Templates

```python
# Staging summary generation
STAGING_SUMMARY_PROMPT = """
You are an expert analyst generating intermediate summaries.

Given the employee profile and a list of tasks with descriptions, comments, and logs:

1. Produce a **clear and comprehensive overview of each task**.
2. **Separate each task overview with a clear divider**, such as "\n\n---\n\n".
3. Capture important details:
   - Task purpose or goal
   - Key actions taken
   - Important comments or notes
   - Issues, blockers, or delays
   - Final outcomes or current status

These overviews will be used for final summary generation, so ensure they are:
- Complete
- Concise but detailed
- Not repetitive
- Easy for another model to read and aggregate

Only output the task overviews.
"""

# Final summary generation
SUMMARY_PROMPT = """
You are an assistant generating a professional year-end self-assessment report for an employee using this overview report.
NOTE: The report should be wysiwyg editor output html(for example tiptap), don't use heading tags inside bullet lists & Return only valid HTML. Do not include ```html ``` or any md formatting.

Using this data, write a clear, concise, and professional self-assessment report strictly 
in first person (using "I", "my", etc.). Do not use third person or passive voice. 
The tone should be reflective, confident, and suitable for HR submission.

---
1. Overview of Work
Summarize the employee's overall contribution this year, based on all projects and tasks.

2. Key Accomplishments
List 2–4 major achievements, using task logs and comments to extract results and outcomes. 
Quantify impact where possible based on insights.

3. Challenges and Resolutions
Identify any major difficulties based on task logs and comments (e.g., technical, collaboration, time pressure) 
and how they were addressed.

4. Skills Developed
Describe new skills or tools the employee learned or improved based on log content and comments.

---
Please write in a professional tone suitable for HR submission. Be concise, but detailed.

Here is the employee's work overviews:
"""

# Content editing prompts
EDIT_PROMPT = """
You are an intelligent assistant. Edit the summary report given to you based on the user requirement mentioned and RAG context. No commentary.
the report is supposed to be wysiwyg editor's html output
"""

EDIT_STAGING_PROMPT = """
Edit the intermediate report based on the user instructions availing RAG tool calling capabilities. 
Add a new paragraph if you don't know where to edit
the output should be wysiwyg editor's html output
"""
```

### Prompt Selection Logic

```python
def get_system_prompt(operation_type: str, staging: bool = False) -> str:
    """Select appropriate prompt based on operation and context."""
    
    if operation_type == "create_staging":
        return STAGING_SUMMARY_PROMPT
    elif operation_type == "create_final":
        return SUMMARY_PROMPT
    elif operation_type == "edit":
        return EDIT_STAGING_PROMPT if staging else EDIT_PROMPT
    else:
        raise ValueError(f"Unknown operation type: {operation_type}")
```

## Token Management and Cost Optimization

### Token Counting

```python
async def get_token_count(self, model, text: str) -> int:
    """Calculate token count for cost estimation."""
    try:
        messages = [{"role": "user", "content": text}]
        return token_counter(model=model, messages=messages)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback estimation (rough approximation)
        return len(text) // 4
```

### Cost Optimization Strategies

1. **Model Selection**: Use appropriate models for different tasks
   - Fast models (Gemini 2.5-flash) for simple edits
   - Powerful models (GPT-4) for complex analysis

2. **Content Chunking**: Process large documents in optimal chunks
3. **Prompt Optimization**: Efficient prompts to minimize token usage
4. **Caching**: Cache responses for repeated queries
5. **Batch Processing**: Group similar requests when possible

## Error Handling and Resilience

### Exception Handling

```python
async def get_response(self, model: str, content: str, user_prompt: str, system_prompt: str, **kwargs):
    try:
        # LLM request logic
        response = await acompletion(...)
        return response.choices[0].message.content
        
    except litellm.RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        # Implement exponential backoff
        await asyncio.sleep(2 ** retry_count)
        raise
        
    except litellm.AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        raise
        
    except litellm.APIError as e:
        logger.error(f"API error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error calling LiteLLM: {e}")
        raise
```

### Retry Logic

```python
async def get_response_with_retry(self, max_retries: int = 3, **kwargs):
    """Get LLM response with exponential backoff retry."""
    
    for attempt in range(max_retries):
        try:
            return await self.get_response(**kwargs)
        except (litellm.RateLimitError, litellm.APIError) as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
```

## Performance Optimization

### Concurrent Processing

```python
async def build_staging_summary(self, request: StagingCreateRequest, action_by: UUID):
    """Process LLM generation and embeddings concurrently."""
    
    # Prepare concurrent operations
    llm_future = self.llm_accessor.get_response(
        model_name, prompt, request.user_prompt, prompts_template.STAGING_SUMMARY_PROMPT
    )
    
    embedding_future = self.embedding_builder.process_and_store_embeddings(
        summary_id=summary_id, content=request.user_data, session=self.session
    )
    
    # Execute concurrently
    llm_text, _ = await asyncio.gather(llm_future, embedding_future)
    
    return self._create_summary(summary_id, llm_text, action_by)
```

### Connection Management

```python
# LiteLLM configuration for optimal performance
litellm.suppress_debug_info = True  # Reduce logging overhead

# Disable verbose logging for production
for key in logging.Logger.manager.loggerDict.keys():
    if "litellm" in key.lower():
        logging.getLogger(key).setLevel(logging.CRITICAL)
```

## Usage Examples

### Basic Summary Generation

```python
# Simple summary generation
llm_accessor = get_llm_accessor()
response = await llm_accessor.get_response(
    model="gemini/gemini-2.5-flash",
    content=user_task_data,
    user_prompt="Focus on technical achievements",
    system_prompt=STAGING_SUMMARY_PROMPT
)
```

### Tool-Assisted Editing

```python
# RAG-enabled editing
tool_schemas, tool_registry = build_tools(summary_id)
response = await llm_accessor.get_response(
    model="gemini/gemini-2.5-flash",
    content=current_summary,
    user_prompt="Add more details about challenges faced",
    system_prompt=EDIT_STAGING_PROMPT,
    use_tools=True,
    tool_schemas=tool_schemas,
    tool_registry=tool_registry
)
```

### Token Cost Estimation

```python
# Estimate costs before processing
token_count = await llm_accessor.get_token_count(
    model="gemini/gemini-2.5-flash",
    text=combined_content
)

estimated_cost = calculate_cost(token_count, model="gemini/gemini-2.5-flash")
logger.info(f"Estimated cost: ${estimated_cost:.4f} for {token_count} tokens")
```

## Monitoring and Analytics

### Usage Tracking

```python
# Track LLM usage for analytics
class LLMUsageTracker:
    def __init__(self):
        self.usage_stats = defaultdict(int)
    
    async def track_request(self, model: str, token_count: int, operation: str):
        self.usage_stats[f"{model}_{operation}"] += token_count
        
        # Log to monitoring system
        logger.info(f"LLM usage: {model} - {operation} - {token_count} tokens")
```

### Performance Metrics

```python
# Monitor response times and success rates
@dataclass
class LLMMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    total_tokens: int = 0
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0
    
    @property
    def average_response_time(self) -> float:
        return self.total_response_time / self.total_requests if self.total_requests > 0 else 0
```

## Best Practices

### 1. Model Selection
- Use fast, cost-effective models for simple tasks
- Reserve powerful models for complex reasoning
- Consider context length requirements
- Test different models for quality vs cost trade-offs

### 2. Prompt Engineering
- Use clear, specific instructions
- Provide examples when helpful
- Structure prompts consistently
- Test prompts with different models

### 3. Tool Integration
- Design tools to be model-agnostic
- Provide clear tool descriptions
- Handle tool errors gracefully
- Limit tool complexity for reliability

### 4. Error Handling
- Implement comprehensive retry logic
- Handle provider-specific errors
- Provide fallback mechanisms
- Log errors for debugging and monitoring

### 5. Performance
- Use concurrent processing where possible
- Implement appropriate caching strategies
- Monitor token usage and costs
- Optimize prompts for efficiency

### 6. Security
- Validate all inputs to LLM calls
- Sanitize outputs before storage
- Implement rate limiting
- Monitor for unusual usage patterns