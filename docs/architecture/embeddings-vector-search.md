# Embeddings and Vector Search Implementation

## Overview

Saaransh Backend implements a sophisticated vector search system using sentence transformers for embedding generation and PostgreSQL's pgvector extension for efficient similarity search. The system enables semantic search across document content, supporting AI-powered features like RAG (Retrieval-Augmented Generation) and content recommendations.

## Architecture Components

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Data     │    │  Content        │    │  Embedding      │
│   (Tasks, Logs, │───▶│  Chunking       │───▶│  Generation     │
│   Comments)     │    │  Pipeline       │    │  (Transformers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query Vector  │    │  Similarity     │    │  Vector         │
│   Generation    │◀───│  Search         │◀───│  Storage        │
│                 │    │  (Cosine)       │    │  (pgvector)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG Tool      │    │  Search Results │    │  Content        │
│   Integration   │    │  Ranking        │    │  Embeddings     │
│                 │    │                 │    │  Table          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

1. **Semantic Understanding**: Convert text to high-dimensional vectors
2. **Efficient Storage**: PostgreSQL pgvector for optimized vector operations
3. **Similarity Search**: Cosine similarity for semantic matching
4. **Content Chunking**: Intelligent text segmentation for optimal embeddings
5. **RAG Integration**: Knowledge base queries for AI-assisted editing
6. **Singleton Pattern**: Efficient model loading and memory management

## Embedding Model Management

### Singleton Pattern Implementation

```python
class EmbeddingModelSingleton:
    _model = None

    @classmethod
    def get_model(cls, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        if cls._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded and ready")
        return cls._model
```

**Benefits:**
- **Memory Efficiency**: Single model instance shared across requests
- **Startup Optimization**: Model loaded once at application startup
- **Resource Management**: Prevents multiple model instances
- **Performance**: Eliminates repeated model loading overhead

### Embedding Model Wrapper

```python
class EmbeddingModel:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.model = EmbeddingModelSingleton.get_model(model_name)

    def embed(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()
```

**Configuration:**
- **Model**: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- **Normalization**: L2 normalization for cosine similarity
- **Output Format**: Python lists for JSON serialization
- **Batch Processing**: Supports multiple texts in single call

### Alternative Models

```python
# High-performance alternative (commented in code)
# class EmbeddingModel:
#     def __init__(self, model_name="BAAI/bge-base-en-v1.5"):
#         self.model = SentenceTransformer(model_name)
```

**Model Comparison:**

| Model | Dimensions | Performance | Use Case |
|-------|------------|-------------|----------|
| `all-mpnet-base-v2` | 768 | Balanced | General purpose, good quality |
| `BAAI/bge-base-en-v1.5` | 768 | High accuracy | Better semantic understanding |
| `all-MiniLM-L6-v2` | 384 | Fast | Lower memory, faster inference |

## Content Chunking Strategy

### Chunking Algorithm

```python
def chunk_task_data(self, user_data: UserData) -> List[str]:
    """Intelligently chunk user task data for optimal embeddings."""
    chunks = []
    
    for i, task in enumerate(user_data.tasks, 1):
        # Main task chunk with employee context
        chunks.append(
            f"{fmt.employee(user_data)} \n "
            f"Task {i} - {task.title} Description: {task.description}"
        )

        # Separate chunk for comments if present
        if task.comments:
            comments_text = (
                f"Task {i} - {task.title} Description: {task.description}\nComments:\n"
                + "\n".join([
                    f"- ({idx+1}) {comment.text}"
                    for idx, comment in enumerate(task.comments)
                ])
            )
            chunks.append(comments_text)

        # Separate chunk for activity logs if present
        if task.logs:
            logs_text = (
                f"Task {i} - {task.title} Description: {task.description}\nActivity Logs:\n"
                + "\n".join([
                    f"- ({idx+1}) {log.content}"
                    for idx, log in enumerate(task.logs)
                ])
            )
            chunks.append(logs_text)

    return chunks
```

### Chunking Strategy Benefits

1. **Semantic Coherence**: Each chunk contains related information
2. **Context Preservation**: Employee info included in each chunk
3. **Granular Search**: Separate chunks for different content types
4. **Optimal Size**: Chunks sized for effective embedding generation
5. **Structured Format**: Consistent formatting for better embeddings

### Example Chunk Structure

```
Employee: John Doe (Role: Senior Software Engineer)

Task 1 - API Development Description: Developed REST API for user management

---

Task 1 - API Development Description: Developed REST API for user management
Comments:
- (1) Implemented OAuth2 authentication
- (2) Added comprehensive error handling
- (3) Achieved 95% test coverage

---

Task 1 - API Development Description: Developed REST API for user management
Activity Logs:
- (1) Started API design phase
- (2) Completed endpoint implementation
- (3) Finished integration testing
```

## Vector Storage and Indexing

### Database Schema

```sql
CREATE TABLE saaransh.content_embeddings (
    embedding_sk BIGINT PRIMARY KEY,             -- Surrogate key
    summary_id UUID,                             -- Associated summary
    chunk_index INTEGER,                         -- Chunk order
    content TEXT NOT NULL,                       -- Original text
    embedding VECTOR(768),                       -- 768-dimensional vector
    is_active BOOLEAN DEFAULT true,              -- Active status
    metadata JSONB,                              -- Additional metadata
    created_at TIMESTAMP DEFAULT NOW()          -- Creation timestamp
);
```

### Vector Indexes

```sql
-- IVFFlat index for cosine similarity
CREATE INDEX content_embeddings_embedding_idx ON saaransh.content_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Supporting indexes
CREATE INDEX content_embeddings_summary_id_idx ON saaransh.content_embeddings(summary_id);
CREATE INDEX content_embeddings_metadata_gin ON saaransh.content_embeddings 
    USING gin (metadata);
```

### Index Configuration

**IVFFlat Parameters:**
- **lists = 100**: Number of clusters for index partitioning
- **vector_cosine_ops**: Optimized for cosine distance operations
- **Maintenance**: Requires periodic REINDEX for optimal performance

**Performance Characteristics:**
- **Query Time**: O(log n) for approximate nearest neighbor
- **Index Size**: ~20% of vector data size
- **Build Time**: O(n log n) for initial index creation

## Embedding Generation Pipeline

### Processing Workflow

```python
async def process_and_store_embeddings(
    self, summary_id: UUID | None, content: UserData, session: AsyncSession
) -> List[ContentEmbedding]:
    """Complete pipeline for embedding generation and storage."""
    
    # 1. Chunk content for optimal embedding
    chunks = self.chunk_task_data(content)
    logger.debug(f"Generated {len(chunks)} text chunks for embedding")

    # 2. Generate embeddings using transformer model
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

    logger.debug(f"Stored {len(results)} embeddings into DB for summary_id={summary_id}")
    return results
```

### Concurrent Processing

```python
# In SummaryBuilder - concurrent LLM and embedding generation
llm_future = self.llm_accessor.get_response(
    model_name, prompt, request.user_prompt, prompts_template.STAGING_SUMMARY_PROMPT
)

embedding_future = self.embedding_builder.process_and_store_embeddings(
    summary_id=summary_id, content=request.user_data, session=self.session
)

# Execute concurrently for optimal performance
llm_text, _ = await asyncio.gather(llm_future, embedding_future)
```

## Similarity Search Implementation

### Vector Search Query

```python
async def find_similar(
    self,
    session: AsyncSession,
    embedding: list[float],
    limit: int = 5,
    summary_id: UUID | None = None
):
    """Find semantically similar content using cosine similarity."""
    
    query = select(self.model)

    # Optional filtering by summary
    if summary_id:
        query = query.where(self.model.summary_id == summary_id)

    # Order by cosine similarity (ascending = most similar first)
    query = query.order_by(self.model.embedding.cosine_distance(embedding))
    query = query.limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
```

### Distance Metrics

**Cosine Distance:**
```sql
-- PostgreSQL pgvector cosine distance
SELECT content, embedding <=> $1 as distance
FROM content_embeddings
ORDER BY embedding <=> $1
LIMIT 10;
```

**Distance Interpretation:**
- **0.0**: Identical vectors (perfect match)
- **0.0-0.3**: Very similar content
- **0.3-0.7**: Moderately similar content
- **0.7-1.0**: Less similar content
- **1.0**: Completely dissimilar (opposite vectors)

### Search Optimization

```python
# Optimized search with filtering
async def search_with_filters(
    self,
    query_vector: List[float],
    summary_id: Optional[UUID] = None,
    min_similarity: float = 0.7,
    limit: int = 10
):
    """Enhanced search with similarity threshold and filtering."""
    
    query = select(
        self.model.content,
        self.model.chunk_index,
        self.model.embedding.cosine_distance(query_vector).label('distance')
    ).where(
        self.model.is_active == True
    )
    
    if summary_id:
        query = query.where(self.model.summary_id == summary_id)
    
    # Filter by similarity threshold
    query = query.where(
        self.model.embedding.cosine_distance(query_vector) <= (1.0 - min_similarity)
    )
    
    query = query.order_by('distance').limit(limit)
    
    result = await session.execute(query)
    return result.all()
```

## RAG Integration

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
            
            # Format results for LLM consumption
            formatted_chunks = [
                f"[Match {i}] (chunk {rec.chunk_index})\n{rec.content}"
                for i, rec in enumerate(results, start=1)
            ]
            
            return "\n\n".join(formatted_chunks)
            
        except Exception as e:
            logger.exception("Error querying knowledge base")
            return f"Error querying knowledge base: {e}"
```

### RAG Workflow

1. **User Query**: User provides editing instructions
2. **Query Embedding**: Convert query to vector representation
3. **Similarity Search**: Find relevant content chunks
4. **Context Assembly**: Format results for LLM
5. **LLM Processing**: Use context to generate better responses
6. **Response Generation**: Return enhanced content

### Example RAG Usage

```python
# In LLM tool calling
{
    "role": "tool",
    "tool_call_id": "call_123",
    "content": """[Match 1] (chunk 0)
Employee: John Doe (Role: Senior Software Engineer)
Task 1 - API Development Description: Developed REST API for user management

[Match 2] (chunk 1)
Task 1 - API Development Description: Developed REST API for user management
Comments:
- (1) Implemented OAuth2 authentication
- (2) Added comprehensive error handling"""
}
```

## Performance Optimization

### Model Loading Optimization

```python
# Application startup - preload embedding model
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load embedding model at startup
    EmbeddingModelSingleton.get_model()
    print("Embedding model loaded at startup")
    
    yield
    
    print("Shutting down Saaransh backend")
```

### Batch Processing

```python
def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Process embeddings in batches for memory efficiency."""
    
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = self.model.encode(
            batch,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()
        all_embeddings.extend(batch_embeddings)
    
    return all_embeddings
```

### Index Maintenance

```sql
-- Periodic index maintenance for optimal performance
REINDEX INDEX content_embeddings_embedding_idx;

-- Update statistics
ANALYZE content_embeddings;

-- Monitor index usage
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan, 
    idx_tup_read
FROM pg_stat_user_indexes 
WHERE tablename = 'content_embeddings';
```

## Monitoring and Analytics

### Embedding Quality Metrics

```python
def calculate_embedding_quality(embeddings: List[List[float]]) -> Dict[str, float]:
    """Calculate quality metrics for generated embeddings."""
    
    import numpy as np
    
    embeddings_array = np.array(embeddings)
    
    # Calculate average cosine similarity between embeddings
    similarities = []
    for i in range(len(embeddings_array)):
        for j in range(i + 1, len(embeddings_array)):
            sim = np.dot(embeddings_array[i], embeddings_array[j])
            similarities.append(sim)
    
    return {
        'mean_similarity': np.mean(similarities),
        'std_similarity': np.std(similarities),
        'embedding_dimension': len(embeddings[0]),
        'num_embeddings': len(embeddings)
    }
```

### Search Performance Monitoring

```python
async def monitor_search_performance(
    query_vector: List[float],
    limit: int = 10
) -> Dict[str, Any]:
    """Monitor vector search performance metrics."""
    
    import time
    
    start_time = time.time()
    
    # Execute search
    results = await content_embedding_accessor.find_similar(
        session=session,
        embedding=query_vector,
        limit=limit
    )
    
    end_time = time.time()
    
    return {
        'query_time_ms': (end_time - start_time) * 1000,
        'results_count': len(results),
        'average_similarity': np.mean([r.distance for r in results]) if results else 0,
        'timestamp': datetime.now().isoformat()
    }
```

## Usage Examples

### Basic Embedding Generation

```python
# Initialize embedding model
embedding_model = EmbeddingModel()

# Generate embeddings for text chunks
texts = ["Sample text 1", "Sample text 2", "Sample text 3"]
embeddings = embedding_model.embed(texts)

print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
```

### Semantic Search

```python
# Search for similar content
query = "API development challenges"
query_vector = embedding_model.embed([query])[0]

similar_chunks = await content_embedding_accessor.find_similar(
    session=session,
    embedding=query_vector,
    limit=5
)

for chunk in similar_chunks:
    print(f"Similarity: {chunk.distance:.3f}")
    print(f"Content: {chunk.content[:100]}...")
```

### RAG-Enhanced Editing

```python
# Use RAG for context-aware editing
user_query = "Add more details about technical challenges"
context = await query_knowledge_base(
    query=user_query,
    summary_id=summary_id,
    top_k=3
)

# Context is automatically used by LLM for better responses
response = await llm_accessor.get_response(
    model="gemini/gemini-2.5-flash",
    content=current_summary,
    user_prompt=user_query,
    system_prompt=EDIT_PROMPT,
    use_tools=True,
    tool_schemas=[tool_query_knowledge_base_definition],
    tool_registry={"query_knowledge_base": query_knowledge_base_wrapper}
)
```

## Best Practices

### 1. Model Selection
- Use appropriate model for your use case and language
- Consider dimension vs performance trade-offs
- Test different models for quality comparison
- Monitor model performance in production

### 2. Chunking Strategy
- Keep chunks semantically coherent
- Include necessary context in each chunk
- Optimize chunk size for your model
- Test chunking strategies with your data

### 3. Index Management
- Choose appropriate index parameters for your data size
- Monitor index performance and rebuild when necessary
- Use appropriate distance metrics for your use case
- Consider memory usage for large datasets

### 4. Search Optimization
- Implement similarity thresholds to filter irrelevant results
- Use appropriate limits to balance quality and performance
- Cache frequently used query vectors
- Monitor search performance and optimize queries

### 5. RAG Integration
- Design tools to provide relevant context
- Format tool responses for optimal LLM consumption
- Handle cases where no relevant context is found
- Monitor RAG effectiveness and iterate on improvements

### 6. Performance
- Preload models at application startup
- Use batch processing for multiple embeddings
- Implement appropriate caching strategies
- Monitor memory usage and optimize as needed