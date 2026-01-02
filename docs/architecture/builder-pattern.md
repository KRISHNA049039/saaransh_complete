# Builder Pattern Implementation

## Overview

Saaransh Backend implements the Builder pattern through its **Builder** classes, which serve as the business logic layer. These classes orchestrate complex operations, enforce business rules, and coordinate between multiple data sources and external services. The Builder pattern encapsulates the construction of complex objects and workflows, providing a clean separation between business logic and data access.

## Architecture

### Business Logic Layer

The Builder classes sit between the API handlers and data accessors, forming the core business logic layer:

```
Handler (API) → Builder (Business Logic) → Accessor (Data Access) → Database/External Services
```

### Key Responsibilities

1. **Complex Object Construction**: Building domain objects with proper validation and business rules
2. **Workflow Orchestration**: Coordinating multi-step business processes
3. **Business Rule Enforcement**: Implementing domain-specific logic and constraints
4. **Service Coordination**: Managing interactions between multiple services and data sources
5. **Transaction Management**: Ensuring data consistency across operations

## Builder Implementations

### 1. SummaryBuilder

The most complex builder, handling AI-powered summary creation and management:

```python
class SummaryBuilder:
    def __init__(self, session: AsyncSession, summary_accessor: SummaryAccessor | None = None, llm_accessor: LLMAccessor | None = None):
        self.session = session
        self.summary_accessor = summary_accessor or SummaryAccessor()
        self.llm_accessor = llm_accessor or get_llm_accessor()
        self.embedding_builder = ContentEmbeddingsBuilder()
```

#### Key Methods

**Staging Summary Creation**
```python
async def build_staging_summary(self, request: StagingCreateRequest, action_by: UUID)
```
- Orchestrates AI summary generation
- Manages concurrent embedding processing
- Handles version control and metadata
- Implements error handling and rollback

**Final Summary Generation**
```python
async def build_summary_from_staging(self, request: SummaryCreateRequest, action_by)
```
- Converts staging summaries to final versions
- Applies user prompts and refinements
- Maintains summary lineage and history

**AI-Powered Editing**
```python
async def edit_summary_via_LLM(self, user_query: str, staging: bool, summary_id: UUID, action_by: UUID, ...)
```
- Integrates with LLM services for content editing
- Supports tool-assisted editing with knowledge base queries
- Manages version transitions and status updates

#### Complex Workflow Example

The staging summary creation demonstrates the Builder pattern's power:

```python
async def build_staging_summary(self, request: StagingCreateRequest, action_by: UUID):
    try:
        # 1. Build prompts from user data
        prompts = await self.build_prompts_not_chunked(request.user_data)
        (prompt, _) = prompts[0]
        
        summary_id = uuid.uuid4()
        model_name = request.model or settings.DEFAULT_LLM_MODEL
        
        # 2. Coordinate concurrent operations
        llm_future = self.llm_accessor.get_response(
            model_name, prompt, request.user_prompt, prompts_template.STAGING_SUMMARY_PROMPT
        )
        
        embedding_future = self.embedding_builder.process_and_store_embeddings(
            summary_id=summary_id, content=request.user_data, session=self.session
        )
        
        # 3. Wait for both operations to complete
        llm_text, _ = await asyncio.gather(llm_future, embedding_future)
        
        # 4. Create domain object with business rules
        summary = Summary(
            summary_id=summary_id,
            content=llm_text,
            meta_data={"model": model_name},
            status_id=SummaryStatus.STAGING,
            effective_from=datetime.now(timezone.utc),
            created_by=action_by,
        )
        
        # 5. Persist to database
        response = await self.summary_accessor.insert(summary, self.session)
        return response
        
    except Exception as e:
        # 6. Handle errors and cleanup
        raise
```

### 2. CommentBuilder

Handles collaborative commenting functionality:

```python
class CommentBuilder:
    def __init__(self, session: AsyncSession, accessor: CommentAccessor | None = None):
        self.session = session
        self.comments_accessor = accessor or CommentAccessor()
```

#### Key Features

**Comment Creation with Validation**
```python
async def build_create(self, request: CommentCreateRequest, action_by: uuid.UUID) -> Comment:
    try:
        if request.summary_id is None:
            raise ValueError("Summary_id is required")
        
        new_comment_id = uuid.uuid4()
        
        model = Comment(
            comment_id=new_comment_id,
            summary_id=request.summary_id,
            content=request.content,
            created_by=action_by,
            effective_from=datetime.now(timezone.utc),
        )
        
        return await self.comments_accessor.insert(model, self.session)
    except Exception as exception:
        logger.error(f"Failed to create comment: {exception}", exc_info=True)
        raise
```

**Comment Editing with Version Control**
```python
async def build_edit(self, request: CommentEditRequest, action_by: uuid.UUID) -> Comment:
    # 1. Validate comment exists
    filters = CommentFetchFilter(comment_id=request.comment_id)
    response = await self.comments_accessor.fetch(session=self.session, filters=filters)
    
    if not response:
        raise Exception("comment doesn't exist")
    
    old_record = response[0]
    
    # 2. Close current version (SCD2 pattern)
    await self.comments_accessor.close_active_record(request.comment_id, self.session)
    
    # 3. Create new version with changes
    model = Comment(
        comment_id=request.comment_id,
        summary_id=old_record.summary_id,
        content=request.content,
        created_by=old_record.created_by,
        modified_by=action_by,
        effective_from=datetime.now(timezone.utc),
    )
    
    return await self.comments_accessor.insert(model, self.session)
```

### 3. UserBuilder

Manages user lifecycle with external service integration:

```python
class UserBuilder:
    def __init__(self, session: AsyncSession, accessor: UserAccessor | None = None):
        self.session = session
        self.user_accessor = accessor or UserAccessor()
        self.kc = get_keycloak_accessor()
```

#### Complex Integration Workflow

**Bulk User Creation with Rollback**
```python
async def build_create_users(self, requests: list[UserCreateRequest], created_by: UUID) -> BulkUserCreateResponse:
    results = []
    any_errors = False
    any_success = False
    
    for request in requests:
        keycloak_user_id = None
        
        try:
            # 1. Create user in Keycloak
            user_name = get_username_from_email(request.user_email)
            kc_user = KeycloakCreateUser(...)
            keycloak_user_id = await self.kc.create_user(kc_user, request.is_admin)
            
            # 2. Create user in local database
            model = User(user_id=keycloak_user_id, ...)
            db_user = await self.user_accessor.insert_commit(model, self.session)
            any_success = True
            
            results.append(UserResponse.model_validate(db_user))
            
        except Exception as e:
            any_errors = True
            
            # 3. Rollback database changes
            try:
                await self.session.rollback()
            except Exception:
                pass
            
            # 4. Cleanup Keycloak user if created
            if keycloak_user_id:
                try:
                    await self.kc.delete_user(keycloak_user_id)
                except Exception as delete_err:
                    logger.error(f"Failed to cleanup Keycloak user: {delete_err}")
            
            # 5. Add error result
            results.append(UserResponse(..., error=str(e)))
    
    return BulkUserCreateResponse(success=not any_errors, partial=any_success and any_errors, results=results)
```

### 4. ContentEmbeddingsBuilder

Specialized builder for AI/ML operations:

```python
class ContentEmbeddingsBuilder:
    def __init__(self):
        self.embedding_accessor = ContentEmbeddingsAccessor()
        self.embedding_model = EmbeddingModel()
```

#### AI Processing Pipeline

**Content Chunking and Embedding**
```python
async def process_and_store_embeddings(self, summary_id: UUID | None, content: UserData, session: AsyncSession) -> List[ContentEmbedding]:
    # 1. Chunk content for optimal embedding
    chunks = self.chunk_task_data(content)
    logger.debug(f"Generated {len(chunks)} text chunks for embedding")
    
    # 2. Generate embeddings using ML model
    embeddings = self.embedding_model.embed(chunks)
    logger.debug(f"Generated {len(embeddings)} embeddings for summary_id={summary_id}")
    
    # 3. Store embeddings with metadata
    results = []
    for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
        record = ContentEmbedding(
            summary_id=summary_id,
            chunk_index=idx,
            content=chunk_text,
            embedding=emb,
            is_active=True,
        )
        inserted = await self.embedding_accessor.insert(record, session)
        results.append(inserted)
    
    return results
```

### 5. SummariesUsersBuilder

Manages complex relationship and permission logic:

```python
class SummariesUsersBuilder:
    def __init__(self, session: AsyncSession, accessor: SummariesUsersAccessor | None = None):
        self.session = session
        self.accessor = accessor or SummariesUsersAccessor()
        self.summary_accessor = SummaryAccessor()
        self.user_accessor = UserAccessor()
```

#### Foreign Key Validation and Relationship Management

```python
async def build_create(self, request: SummariesUsersCreateRequest, action_by: uuid.UUID) -> SummariesUsers:
    try:
        # 1. Validate foreign key relationships
        await self._fk_validator(request.summary_id, request.user_id)
        
        # 2. Create relationship with proper metadata
        model = SummariesUsers(
            summary_id=request.summary_id,
            user_id=request.user_id,
            role_id=request.role_id,
            created_by=action_by,
            created_date=datetime.now(timezone.utc),
        )
        
        return await self.accessor.insert(model, self.session)
        
    except Exception as exc:
        logger.error(f"Failed to create summaries_users entry: {exc}", exc_info=True)
        raise

async def _fk_validator(self, summary_id: uuid.UUID, user_id: uuid.UUID):
    # Validate summary exists and is active
    summary = await self.summary_accessor.get_by_summary_id(
        session=self.session, summary_id=summary_id, effective_only=True, is_active=True
    )
    if summary is None:
        raise ValueError(f"Summary {summary_id} does not exist or is inactive")
    
    # Validate user exists and is active
    user = await self.user_accessor.get_by_user_id(
        session=self.session, user_id=user_id, effective_only=True, is_active=True
    )
    if user is None:
        raise ValueError(f"User {user_id} does not exist or is inactive")
```

## Design Patterns Within Builders

### 1. Dependency Injection

Builders use constructor injection for loose coupling:

```python
class SummaryBuilder:
    def __init__(self, session: AsyncSession, summary_accessor: SummaryAccessor | None = None, llm_accessor: LLMAccessor | None = None):
        self.session = session
        self.summary_accessor = summary_accessor or SummaryAccessor()
        self.llm_accessor = llm_accessor or get_llm_accessor()
```

### 2. Factory Pattern Integration

Builders integrate with factory patterns for service creation:

```python
self.llm_accessor = llm_accessor or get_llm_accessor()  # Factory method
self.kc = get_keycloak_accessor()  # Factory method
```

### 3. Strategy Pattern

Different strategies for different operations:

```python
# Different prompts for different operations
if staging:
    system_prompt = prompts_template.EDIT_STAGING_PROMPT
else:
    system_prompt = prompts_template.EDIT_PROMPT
```

### 4. Template Method Pattern

Common workflow structure with customizable steps:

```python
# Common pattern: validate → process → persist → handle errors
async def build_create(self, request, action_by):
    try:
        # 1. Validation
        self._validate_request(request)
        
        # 2. Business logic processing
        model = self._create_model(request, action_by)
        
        # 3. Persistence
        result = await self.accessor.insert(model, self.session)
        
        return result
    except Exception as e:
        # 4. Error handling
        logger.error(f"Operation failed: {e}")
        raise
```

## Key Benefits

### 1. Business Logic Encapsulation

- **Centralized Rules**: All business logic in one place
- **Consistent Behavior**: Same rules applied across all entry points
- **Easy Maintenance**: Changes in one location affect entire system

### 2. Complex Workflow Management

- **Multi-Step Operations**: Coordinate complex sequences
- **Error Handling**: Comprehensive rollback and cleanup
- **Async Coordination**: Manage concurrent operations efficiently

### 3. Service Integration

- **External Services**: Seamless integration with Keycloak, LLM services
- **Data Consistency**: Maintain consistency across multiple systems
- **Failure Recovery**: Handle partial failures gracefully

### 4. Testability

- **Isolated Testing**: Test business logic without external dependencies
- **Mock Integration**: Easy to mock accessors and external services
- **Unit Testing**: Test individual workflows independently

### 5. Maintainability

- **Single Responsibility**: Each builder handles one domain
- **Clear Interfaces**: Well-defined input/output contracts
- **Extensibility**: Easy to add new operations and workflows

## Usage Patterns

### 1. Simple CRUD Operations

```python
# In handler
builder = CommentBuilder(session)
comment = await builder.build_create(request, user_id)
```

### 2. Complex Multi-Service Operations

```python
# In handler
builder = UserBuilder(session)
result = await builder.build_create_users(requests, admin_id)
```

### 3. AI-Powered Workflows

```python
# In handler
builder = SummaryBuilder(session, llm_accessor=llm_service)
summary = await builder.build_staging_summary(request, user_id)
```

### 4. Relationship Management

```python
# In handler
builder = SummariesUsersBuilder(session)
relationship = await builder.build_create(share_request, owner_id)
```

## Best Practices

### 1. Constructor Design
- Use dependency injection for testability
- Provide sensible defaults for optional dependencies
- Initialize all required services in constructor

### 2. Error Handling
- Use comprehensive try-catch blocks
- Log errors with context information
- Implement proper rollback mechanisms
- Clean up external resources on failure

### 3. Transaction Management
- Use database sessions appropriately
- Implement proper commit/rollback logic
- Handle partial failures in bulk operations

### 4. Async Operations
- Use asyncio.gather() for concurrent operations
- Handle async exceptions properly
- Optimize for performance with parallel processing

### 5. Validation
- Validate inputs early in the process
- Check foreign key relationships
- Enforce business rules consistently