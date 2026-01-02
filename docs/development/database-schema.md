# Database Schema and Data Models

## Overview

Saaransh Backend uses a sophisticated PostgreSQL database schema with advanced features including vector embeddings (pgvector), JSON storage, and Slowly Changing Dimensions Type 2 (SCD2) for comprehensive data versioning. The schema is designed to support AI-powered summarization, collaborative editing, and complete audit trails.

## Database Architecture

### Technology Stack

- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0 with async support
- **Vector Extension**: pgvector for semantic similarity search
- **Schema Management**: Alembic migrations
- **Connection Pool**: asyncpg with connection pooling

### Schema Organization

```
saaransh (schema)
├── users                    # User accounts and profiles
├── summaries               # AI-generated summaries with versioning
├── comments                # Collaborative feedback with versioning
├── summaries_users         # Sharing and permissions
├── user_prompts           # AI interaction history
└── content_embeddings     # Vector embeddings for semantic search
```

## Core Data Models

### 1. Users Table

**Purpose**: Store user account information with complete version history.

```sql
CREATE TABLE saaransh.users (
    user_sk BIGINT PRIMARY KEY,                    -- Surrogate key (auto-increment)
    user_id UUID NOT NULL,                        -- Business key (from Keycloak)
    user_name VARCHAR,                             -- Username (from email)
    user_email VARCHAR,                            -- Email address
    first_name VARCHAR,                            -- First name
    last_name VARCHAR,                             -- Last name
    is_active BOOLEAN NOT NULL DEFAULT true,      -- Account status
    is_admin BOOLEAN,                              -- Admin privileges
    entity_type_id BIGINT NOT NULL DEFAULT 0,     -- Entity classification
    created_by UUID,                               -- Creator user ID
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by UUID,                              -- Last modifier user ID
    effective_from TIMESTAMP,                      -- SCD2 start date
    effective_to TIMESTAMP                         -- SCD2 end date (NULL = current)
);

-- Indexes
CREATE INDEX idx_users_user_id ON saaransh.users(user_id);
CREATE INDEX idx_users_email ON saaransh.users(user_email);
CREATE INDEX idx_users_effective ON saaransh.users(effective_to);
```

**Key Features**:
- **SCD2 Versioning**: Complete history of user changes
- **Keycloak Integration**: `user_id` matches Keycloak UUID
- **Admin Role Tracking**: Local admin status synchronized with Keycloak
- **Audit Trail**: Track who created/modified each record

### 2. Summaries Table

**Purpose**: Store AI-generated summaries with comprehensive versioning and metadata.

```sql
CREATE TABLE saaransh.summaries (
    summary_sk BIGINT PRIMARY KEY,                -- Surrogate key (auto-increment)
    summary_id UUID NOT NULL,                     -- Business key
    content TEXT,                                 -- Summary content (HTML)
    start_date TIMESTAMP,                         -- Summary period start
    end_date TIMESTAMP,                           -- Summary period end
    status_id BIGINT,                             -- Summary status (0-5)
    metadata JSONB,                               -- Model info, settings, etc.
    is_active BOOLEAN NOT NULL DEFAULT true,     -- Active status
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,                              -- Creator user ID
    modified_by UUID,                             -- Last modifier user ID
    effective_from TIMESTAMP,                     -- SCD2 start date
    effective_to TIMESTAMP,                       -- SCD2 end date (NULL = current)
    entity_type_id BIGINT NOT NULL DEFAULT 1     -- Entity classification
);

-- Indexes
CREATE INDEX idx_summaries_summary_id ON saaransh.summaries(summary_id);
CREATE INDEX idx_summaries_status ON saaransh.summaries(status_id);
CREATE INDEX idx_summaries_effective ON saaransh.summaries(effective_to);
CREATE INDEX idx_summaries_created_by ON saaransh.summaries(created_by);
```

**Key Features**:
- **Content Storage**: HTML content from WYSIWYG editors
- **Status Tracking**: Lifecycle management (staging → final)
- **Metadata Storage**: JSON metadata for AI model info, settings
- **Version Control**: Complete edit history with SCD2

### 3. Comments Table

**Purpose**: Store collaborative feedback on summaries with full version history.

```sql
CREATE TABLE saaransh.comments (
    comment_sk BIGINT PRIMARY KEY,                -- Surrogate key (auto-increment)
    comment_id UUID NOT NULL,                     -- Business key
    summary_id UUID,                              -- Foreign key to summaries
    content TEXT,                                 -- Comment content
    is_active BOOLEAN NOT NULL DEFAULT true,     -- Active status
    created_by UUID,                              -- Creator user ID
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by UUID,                             -- Last modifier user ID
    effective_from TIMESTAMP,                     -- SCD2 start date
    effective_to TIMESTAMP,                       -- SCD2 end date (NULL = current)
    entity_type_id BIGINT NOT NULL DEFAULT 4     -- Entity classification
);

-- Indexes
CREATE INDEX idx_comments_comment_id ON saaransh.comments(comment_id);
CREATE INDEX idx_comments_summary_id ON saaransh.comments(summary_id);
CREATE INDEX idx_comments_effective ON saaransh.comments(effective_to);
```

**Key Features**:
- **Summary Association**: Link comments to specific summaries
- **Edit History**: Track all comment modifications
- **User Attribution**: Track comment authors and editors

### 4. Summaries Users Table

**Purpose**: Manage summary sharing and role-based permissions.

```sql
CREATE TABLE saaransh.summaries_users (
    summaries_users_sk BIGINT PRIMARY KEY,       -- Surrogate key (auto-increment)
    summary_id UUID,                              -- Foreign key to summaries
    user_id UUID,                                 -- Foreign key to users
    role_id BIGINT,                               -- Role (0=OWNER, 1=EDITOR, 2=VIEWER, 3=ADMIN)
    reviewed BOOLEAN,                             -- Has user reviewed the summary
    is_active BOOLEAN NOT NULL DEFAULT true,     -- Active status
    created_by UUID,                              -- Who shared the summary
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_summaries_users_summary_id ON saaransh.summaries_users(summary_id);
CREATE INDEX idx_summaries_users_user_id ON saaransh.summaries_users(user_id);
CREATE UNIQUE INDEX idx_summaries_users_unique ON saaransh.summaries_users(summary_id, user_id) 
    WHERE is_active = true;
```

**Key Features**:
- **Role-Based Access**: Fine-grained permission control
- **Sharing Tracking**: Audit who shared what with whom
- **Review Status**: Track user engagement with shared summaries
- **Unique Constraints**: Prevent duplicate active sharing records

### 5. User Prompts Table

**Purpose**: Track AI interaction history for audit and analysis.

```sql
CREATE TABLE saaransh.user_prompts (
    user_prompt_sk BIGINT PRIMARY KEY,           -- Surrogate key (auto-increment)
    content TEXT,                                -- User prompt text
    summary_id UUID,                             -- Associated summary
    metadata JSONB,                              -- Additional prompt metadata
    is_active BOOLEAN NOT NULL DEFAULT true,    -- Active status
    created_by UUID,                             -- User who created prompt
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entity_type_id BIGINT NOT NULL DEFAULT 5    -- Entity classification
);

-- Indexes
CREATE INDEX idx_user_prompts_summary_id ON saaransh.user_prompts(summary_id);
CREATE INDEX idx_user_prompts_created_by ON saaransh.user_prompts(created_by);
```

**Key Features**:
- **AI Interaction Tracking**: Complete history of user-AI interactions
- **Summary Association**: Link prompts to specific summaries
- **Metadata Storage**: Additional context and parameters
- **No Versioning**: Append-only for audit trail

### 6. Content Embeddings Table

**Purpose**: Store vector embeddings for semantic similarity search.

```sql
CREATE TABLE saaransh.content_embeddings (
    embedding_sk BIGINT PRIMARY KEY,             -- Surrogate key (auto-increment)
    summary_id UUID,                             -- Associated summary
    chunk_index INTEGER,                         -- Chunk order within summary
    content TEXT NOT NULL,                       -- Original text content
    embedding VECTOR(768),                       -- 768-dimensional vector
    is_active BOOLEAN DEFAULT true,              -- Active status
    metadata JSONB,                              -- Additional embedding metadata
    created_at TIMESTAMP DEFAULT NOW()          -- Creation timestamp
);

-- Vector similarity indexes
CREATE INDEX content_embeddings_embedding_idx ON saaransh.content_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Additional indexes
CREATE INDEX content_embeddings_summary_id_idx ON saaransh.content_embeddings(summary_id);
CREATE INDEX content_embeddings_metadata_gin ON saaransh.content_embeddings 
    USING gin (metadata);
```

**Key Features**:
- **Vector Storage**: 768-dimensional embeddings using pgvector
- **Chunked Content**: Support for large documents split into chunks
- **Similarity Search**: Optimized indexes for cosine similarity
- **Metadata Support**: JSON metadata with GIN indexing

## Entity Relationships

### Relationship Diagram

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│    Users    │    │ Summaries_Users │    │  Summaries  │
│             │◀──▶│   (Many-Many)   │◀──▶│             │
│ user_id (PK)│    │                 │    │summary_id(PK)│
└─────────────┘    └─────────────────┘    └─────────────┘
       │                                          │
       │                                          ▼
       │                                  ┌─────────────┐
       │                                  │  Comments   │
       │                                  │             │
       │                                  │summary_id(FK)│
       │                                  └─────────────┘
       │                                          │
       ▼                                          ▼
┌─────────────┐                          ┌─────────────┐
│User_Prompts │                          │Content_     │
│             │                          │Embeddings   │
│summary_id(FK)│                          │             │
│created_by(FK)│                          │summary_id(FK)│
└─────────────┘                          └─────────────┘
```

### Key Relationships

1. **Users ↔ Summaries** (Many-to-Many via Summaries_Users)
   - Users can own, edit, or view multiple summaries
   - Summaries can be shared with multiple users
   - Role-based permissions control access level

2. **Summaries → Comments** (One-to-Many)
   - Each summary can have multiple comments
   - Comments are linked to specific summary versions

3. **Users → Comments** (One-to-Many)
   - Users can create multiple comments
   - Comment authorship and editing tracked

4. **Summaries → Content_Embeddings** (One-to-Many)
   - Each summary generates multiple embedding chunks
   - Embeddings enable semantic search across summaries

5. **Users → User_Prompts** (One-to-Many)
   - Track all AI interactions per user
   - Audit trail for AI usage and patterns

## SCD2 Implementation

### Slowly Changing Dimensions Type 2

Three tables implement SCD2 for complete version history:

- **Users**: Track profile changes, role modifications
- **Summaries**: Track content edits, status changes
- **Comments**: Track comment edits and modifications

### SCD2 Pattern

```sql
-- Current record (active version)
SELECT * FROM summaries 
WHERE summary_id = 'uuid' AND effective_to IS NULL;

-- All versions (complete history)
SELECT * FROM summaries 
WHERE summary_id = 'uuid' 
ORDER BY effective_from DESC;

-- Point-in-time query
SELECT * FROM summaries 
WHERE summary_id = 'uuid' 
  AND effective_from <= '2024-01-15T12:00:00Z'
  AND (effective_to IS NULL OR effective_to > '2024-01-15T12:00:00Z');
```

### Version Management Process

```python
# 1. Close current version
UPDATE summaries 
SET effective_to = NOW() 
WHERE summary_id = 'uuid' AND effective_to IS NULL;

# 2. Insert new version
INSERT INTO summaries (
    summary_id,           -- Same business key
    content,              -- New content
    effective_from,       -- NOW()
    effective_to,         -- NULL (new active version)
    created_by,           -- Original creator
    modified_by           -- Current modifier
) VALUES (...);
```

## Data Types and Constraints

### PostgreSQL Data Types

| SQLAlchemy Type | PostgreSQL Type | Usage |
|-----------------|-----------------|-------|
| `BigInteger` | `BIGINT` | Primary keys, foreign keys |
| `UUID` | `UUID` | Business keys, user IDs |
| `String` | `VARCHAR` | Text fields with length limits |
| `Text` | `TEXT` | Unlimited text content |
| `Boolean` | `BOOLEAN` | Status flags, permissions |
| `DateTime` | `TIMESTAMP` | Timestamps with timezone |
| `JSON` | `JSONB` | Structured metadata |
| `Vector(768)` | `VECTOR(768)` | Embedding vectors |

### Constraints and Validation

```sql
-- Primary key constraints
ALTER TABLE summaries ADD CONSTRAINT pk_summaries PRIMARY KEY (summary_sk);

-- Foreign key constraints
ALTER TABLE comments ADD CONSTRAINT fk_comments_summary 
    FOREIGN KEY (summary_id) REFERENCES summaries(summary_id);

-- Check constraints
ALTER TABLE summaries ADD CONSTRAINT chk_summaries_status 
    CHECK (status_id BETWEEN 0 AND 5);

-- Unique constraints
ALTER TABLE summaries_users ADD CONSTRAINT uk_summaries_users 
    UNIQUE (summary_id, user_id) WHERE is_active = true;
```

## Indexing Strategy

### Performance Indexes

```sql
-- Primary access patterns
CREATE INDEX idx_summaries_user_access ON summaries(created_by, effective_to);
CREATE INDEX idx_comments_summary_timeline ON comments(summary_id, created_date);

-- Search and filtering
CREATE INDEX idx_users_email_active ON users(user_email) WHERE is_active = true;
CREATE INDEX idx_summaries_status_active ON summaries(status_id) WHERE is_active = true;

-- Vector similarity (pgvector)
CREATE INDEX idx_embeddings_cosine ON content_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- JSON metadata (GIN)
CREATE INDEX idx_summaries_metadata ON summaries USING gin (metadata);
CREATE INDEX idx_embeddings_metadata ON content_embeddings USING gin (metadata);
```

### Index Maintenance

- **VACUUM**: Regular maintenance for deleted records
- **REINDEX**: Periodic rebuilding of vector indexes
- **ANALYZE**: Update statistics for query optimization

## Data Migration and Versioning

### Alembic Integration

```python
# Migration example
def upgrade():
    # Add new column with default
    op.add_column('summaries', 
        sa.Column('new_field', sa.String(255), nullable=True))
    
    # Update existing records
    op.execute("UPDATE summaries SET new_field = 'default_value'")
    
    # Make column non-nullable
    op.alter_column('summaries', 'new_field', nullable=False)

def downgrade():
    op.drop_column('summaries', 'new_field')
```

### Schema Evolution

1. **Backward Compatible**: Add optional columns
2. **Data Migration**: Transform existing data
3. **Index Management**: Add/remove indexes as needed
4. **Constraint Updates**: Modify validation rules

## Query Patterns

### Common Query Examples

#### 1. User's Accessible Summaries
```sql
SELECT s.*, su.role_id
FROM summaries s
JOIN summaries_users su ON s.summary_id = su.summary_id
WHERE su.user_id = $1 
  AND su.is_active = true 
  AND s.effective_to IS NULL
  AND s.is_active = true
ORDER BY s.created_date DESC;
```

#### 2. Summary with Comments
```sql
SELECT 
    s.summary_id,
    s.content as summary_content,
    c.comment_id,
    c.content as comment_content,
    c.created_by as comment_author
FROM summaries s
LEFT JOIN comments c ON s.summary_id = c.summary_id 
    AND c.effective_to IS NULL
WHERE s.summary_id = $1 
  AND s.effective_to IS NULL
ORDER BY c.created_date ASC;
```

#### 3. Semantic Similarity Search
```sql
SELECT 
    ce.summary_id,
    ce.content,
    ce.embedding <=> $1 as similarity_score
FROM content_embeddings ce
WHERE ce.is_active = true
ORDER BY ce.embedding <=> $1
LIMIT 10;
```

#### 4. User Activity Audit
```sql
SELECT 
    'summary' as entity_type,
    summary_id as entity_id,
    created_date as activity_date,
    created_by as user_id,
    'created' as action
FROM summaries
WHERE created_by = $1

UNION ALL

SELECT 
    'comment' as entity_type,
    comment_id as entity_id,
    created_date as activity_date,
    created_by as user_id,
    'commented' as action
FROM comments
WHERE created_by = $1

ORDER BY activity_date DESC;
```

## Performance Considerations

### Query Optimization

1. **Effective Date Filtering**: Always filter on `effective_to IS NULL` for current records
2. **Composite Indexes**: Create indexes matching common WHERE clauses
3. **Partial Indexes**: Use WHERE clauses in indexes for filtered queries
4. **Vector Index Tuning**: Adjust `lists` parameter based on data size

### Connection Management

```python
# Connection pool configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Base connection pool size
    max_overflow=10,        # Additional connections when needed
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600,      # Recycle connections every hour
)
```

### Monitoring Queries

```sql
-- Long-running queries
SELECT query, query_start, state, wait_event_type
FROM pg_stat_activity 
WHERE state = 'active' AND query_start < NOW() - INTERVAL '1 minute';

-- Index usage statistics
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes 
WHERE schemaname = 'saaransh'
ORDER BY idx_scan DESC;

-- Table size and bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'saaransh'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Security Considerations

### Row-Level Security (RLS)

```sql
-- Enable RLS on sensitive tables
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;

-- Policy for user access
CREATE POLICY summaries_user_access ON summaries
    FOR ALL TO application_role
    USING (
        summary_id IN (
            SELECT summary_id FROM summaries_users 
            WHERE user_id = current_setting('app.current_user_id')::uuid
              AND is_active = true
        )
    );
```

### Data Encryption

- **At Rest**: PostgreSQL TDE (Transparent Data Encryption)
- **In Transit**: SSL/TLS connections
- **Application Level**: Sensitive fields encrypted before storage

### Audit Logging

```sql
-- Audit trigger example
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        table_name,
        operation,
        old_values,
        new_values,
        user_id,
        timestamp
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        row_to_json(OLD),
        row_to_json(NEW),
        current_setting('app.current_user_id')::uuid,
        NOW()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

## Backup and Recovery

### Backup Strategy

1. **Full Backups**: Daily pg_dump of entire database
2. **Incremental**: WAL archiving for point-in-time recovery
3. **Vector Indexes**: Special handling for pgvector indexes
4. **Metadata**: Backup schema definitions and migrations

### Recovery Procedures

```bash
# Point-in-time recovery
pg_basebackup -D /backup/base -Ft -z -P
# Restore to specific timestamp
# Configure recovery.conf with target time
```

## Best Practices

### 1. Schema Design
- Use surrogate keys for all tables
- Implement SCD2 for audit-critical tables
- Normalize data appropriately
- Use appropriate data types and constraints

### 2. Query Performance
- Always filter on effective_to for current records
- Use appropriate indexes for query patterns
- Monitor and optimize slow queries
- Regular VACUUM and ANALYZE

### 3. Data Integrity
- Implement foreign key constraints
- Use check constraints for data validation
- Regular consistency checks
- Proper transaction management

### 4. Maintenance
- Regular index maintenance
- Monitor table bloat
- Archive old data appropriately
- Keep statistics up to date