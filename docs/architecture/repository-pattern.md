# Repository Pattern Implementation

## Overview

Saaransh Backend implements the Repository pattern through its **Accessor** classes, which provide a clean abstraction layer between the business logic and data persistence. This pattern encapsulates the logic needed to access data sources, centralizing common data access functionality and promoting better maintainability and testability.

## Architecture

### Base Repository (BaseDBAccessor)

The foundation of the Repository pattern is the `BaseDBAccessor` class, which provides common database operations for all entities:

```python
class BaseDBAccessor(Generic[ModelType]):
    model: Type[ModelType]
    
    async def fetch(self, session: AsyncSession, filters: Optional[BaseModel] = None, sort: Optional[SortQuery] = None)
    def apply_filters_and_sort(self, query, filters, sort)
    def _apply_scd2_filter(self, query, filters)
    def _apply_filters(self, query, filters)
    def _apply_sort(self, query, sort)
```

### Key Features

1. **Generic Type Safety**: Uses Python generics to ensure type safety across different models
2. **SCD2 Support**: Built-in support for Slowly Changing Dimensions Type 2 for data versioning
3. **Flexible Filtering**: Dynamic filter application based on model attributes
4. **Sorting & Pagination**: Comprehensive sorting with null handling
5. **Async Operations**: Full async/await support for high performance

## Repository Implementations

### 1. SummaryAccessor

Handles all summary-related database operations:

```python
class SummaryAccessor(BaseDBAccessor[Summary]):
    model = Summary
    
    async def close_active_record(self, summary_id, session: AsyncSession)
    async def insert(self, summary: Summary, session: AsyncSession) -> Summary
    async def get_by_summary_id(self, session: AsyncSession, summary_id: UUID, *, effective_only: bool = True, is_active: bool = True) -> Optional[Summary]
```

**Key Responsibilities:**
- Summary CRUD operations
- Version management through SCD2 protocol
- Active record lifecycle management
- Summary-specific query optimizations

### 2. CommentAccessor

Manages comment data persistence:

```python
class CommentAccessor(BaseDBAccessor[Comment]):
    model = Comment
    
    async def close_active_record(self, comment_id, session: AsyncSession)
    async def insert(self, comment: Comment, session: AsyncSession) -> Comment
```

**Key Responsibilities:**
- Comment creation and modification
- Comment lifecycle management
- Relationship handling with summaries

### 3. UserAccessor

Handles user data operations:

```python
class UserAccessor(BaseDBAccessor[User]):
    model = User
    
    async def close_active_record(self, user_id: UUID, session: AsyncSession)
    async def insert_commit(self, model: User, session: AsyncSession) -> User
    async def insert_flush(self, model: User, session: AsyncSession) -> User
    async def get_active_by_email(self, email: str, session: AsyncSession) -> User | None
    async def get_active_by_username(self, username: str, session: AsyncSession) -> User | None
    async def get_by_user_id(self, session: AsyncSession, user_id: UUID, *, effective_only: bool = True, is_active: bool = True) -> Optional[User]
```

**Key Responsibilities:**
- User authentication data management
- User profile operations
- Email and username uniqueness enforcement
- User lifecycle management

### 4. ContentEmbeddingsAccessor

Specialized repository for vector embeddings:

```python
class ContentEmbeddingsAccessor(BaseDBAccessor[ContentEmbedding]):
    model = ContentEmbedding
    
    async def insert(self, embedding_obj: ContentEmbedding, session: AsyncSession) -> ContentEmbedding
    async def find_similar(self, session: AsyncSession, embedding: list[float], limit: int = 5, summary_id: UUID | None = None)
```

**Key Responsibilities:**
- Vector embedding storage
- Semantic similarity search using pgvector
- Cosine distance calculations
- Content-based recommendations

## SCD2 Protocol Integration

### Slowly Changing Dimensions Type 2

The Repository pattern integrates with SCD2 protocol for data versioning:

```python
class SCD2Model(Protocol):
    effective_to: Any

class SCD2Filter(BaseModel):
    effective_only: bool = True
```

**Benefits:**
- **Historical Data Preservation**: All changes are tracked with timestamps
- **Point-in-Time Queries**: Retrieve data as it existed at any point in time
- **Audit Trail**: Complete history of all modifications
- **Data Integrity**: No data loss during updates

### SCD2 Implementation

1. **Active Records**: Records with `effective_to = NULL` are current
2. **Historical Records**: Records with `effective_to` timestamp are historical
3. **Version Control**: Each change creates a new record while preserving the old one
4. **Automatic Filtering**: Base accessor automatically filters for active records

## Advanced Features

### 1. Dynamic Filtering

The base accessor supports dynamic filtering based on model attributes:

```python
def _apply_filters(self, query, filters):
    if not filters:
        return query
    
    for key, value in filters.model_dump(exclude_none=True).items():
        if key == "effective_only":
            continue
        
        if hasattr(self.model, key):
            query = query.where(getattr(self.model, key) == value)
    
    return query
```

### 2. Flexible Sorting

Comprehensive sorting with null handling:

```python
def _apply_sort(self, query, sort):
    if not sort or not sort.sorts:
        return query
    
    orders = []
    for rule in sort.sorts:
        if hasattr(self.model, rule.field):
            col = getattr(self.model, rule.field)
            order = desc(col) if rule.direction == SortDirection.DESC else asc(col)
            
            if rule.nulls == NullsPosition.FIRST:
                order = nullsfirst(order)
            elif rule.nulls == NullsPosition.LAST:
                order = nullslast(order)
            
            orders.append(order)
    
    if orders:
        query = query.order_by(*orders)
    
    return query
```

### 3. Vector Similarity Search

Specialized functionality for AI-powered features:

```python
async def find_similar(self, session: AsyncSession, embedding: list[float], limit: int = 5, summary_id: UUID | None = None):
    query = select(self.model)
    
    if summary_id:
        query = query.where(self.model.summary_id == summary_id)
    
    query = query.order_by(self.model.embedding.cosine_distance(embedding))
    query = query.limit(limit)
    
    result = await session.execute(query)
    return result.scalars().all()
```

## Benefits of This Implementation

### 1. Separation of Concerns
- **Business Logic**: Isolated in Builder classes
- **Data Access**: Centralized in Accessor classes
- **Data Models**: Pure data structures without business logic

### 2. Testability
- **Mock-Friendly**: Easy to mock accessor interfaces for unit testing
- **Isolated Testing**: Test business logic without database dependencies
- **Integration Testing**: Test data access logic independently

### 3. Maintainability
- **Single Responsibility**: Each accessor handles one entity type
- **DRY Principle**: Common functionality in base class
- **Consistent Interface**: Uniform API across all repositories

### 4. Performance
- **Async Operations**: Non-blocking database operations
- **Query Optimization**: Specialized queries for each entity
- **Connection Pooling**: Efficient database connection management

### 5. Extensibility
- **Generic Base**: Easy to add new entity repositories
- **Customizable**: Override base methods for specific needs
- **Plugin Architecture**: Add new functionality without breaking existing code

## Usage Patterns

### 1. Basic CRUD Operations

```python
# In a Builder class
async def create_summary(self, request: SummaryCreateRequest, user_id: UUID):
    accessor = SummaryAccessor()
    summary = Summary(...)
    return await accessor.insert(summary, session)
```

### 2. Complex Queries with Filtering

```python
# Fetch summaries with filters and sorting
filters = SummaryFetchFilter(status=SummaryStatus.SUBMITTED)
sort_query = sort_by("-created_date")
summaries = await accessor.fetch(session, filters, sort_query)
```

### 3. Version Management

```python
# Close current version and create new one
await accessor.close_active_record(summary_id, session)
new_summary = Summary(...)
await accessor.insert(new_summary, session)
```

## Best Practices

### 1. Repository Design
- Keep repositories focused on single entity types
- Use base class for common functionality
- Implement entity-specific methods as needed

### 2. Error Handling
- Handle database exceptions at the accessor level
- Provide meaningful error messages
- Use proper transaction management

### 3. Performance Optimization
- Use appropriate indexes for query patterns
- Implement query optimization for complex operations
- Consider caching for frequently accessed data

### 4. Testing Strategy
- Unit test each repository method
- Mock external dependencies
- Test error conditions and edge cases