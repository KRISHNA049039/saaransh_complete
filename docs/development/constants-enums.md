# Constants and Enums

## Overview

Saaransh Backend uses a centralized constants system to maintain consistency across the application. Constants are organized into logical classes and used throughout the system for role-based access control, summary lifecycle management, and entity classification.

## System Constants

### 1. User Roles (Roles Class)

The `Roles` class defines the role-based access control hierarchy used throughout the collaboration system.

```python
class Roles:
    OWNER = 0      # Full control over summary
    EDITOR = 1     # Can edit content and add comments
    VIEWER = 2     # Read-only access with commenting
    ADMIN = 3      # System-wide administrative privileges
```

#### Role Hierarchy and Permissions

| Role | Value | Permissions | Use Cases |
|------|-------|-------------|-----------|
| **OWNER** | 0 | • Edit summary content<br>• Share with other users<br>• Manage permissions<br>• Delete summary<br>• View all versions | • Summary creator<br>• Project lead<br>• Content owner |
| **EDITOR** | 1 | • Edit summary content<br>• Add/edit comments<br>• View all versions<br>• Cannot share or manage permissions | • Team members<br>• Collaborators<br>• Content contributors |
| **VIEWER** | 2 | • Read summary content<br>• Add comments<br>• View current version only<br>• Cannot edit content | • Stakeholders<br>• Reviewers<br>• Read-only access |
| **ADMIN** | 3 | • All OWNER permissions<br>• System-wide access<br>• User management<br>• Override permissions | • System administrators<br>• IT support<br>• Compliance officers |

#### Usage Examples

```python
# In summaries handler - assign owner role to creator
from app.models.constants import Roles

role_request = SummariesUsersCreateRequest(
    summary_id=response.summary_id,
    user_id=requested_by,
    role_id=Roles.OWNER,  # Creator gets owner role
)

# In access control logic
def can_edit_summary(user_role: int) -> bool:
    return user_role in [Roles.OWNER, Roles.EDITOR, Roles.ADMIN]

def can_share_summary(user_role: int) -> bool:
    return user_role in [Roles.OWNER, Roles.ADMIN]

def can_manage_permissions(user_role: int) -> bool:
    return user_role in [Roles.OWNER, Roles.ADMIN]
```

#### Role Assignment Patterns

```python
# Default role assignment
DEFAULT_CREATOR_ROLE = Roles.OWNER
DEFAULT_SHARED_ROLE = Roles.VIEWER

# Role validation
VALID_ROLES = [Roles.OWNER, Roles.EDITOR, Roles.VIEWER, Roles.ADMIN]

def validate_role(role_id: int) -> bool:
    return role_id in VALID_ROLES

# Role hierarchy check (lower number = higher privileges)
def has_higher_or_equal_role(user_role: int, required_role: int) -> bool:
    return user_role <= required_role
```

### 2. Summary Status (SummaryStatus Class)

The `SummaryStatus` class defines the complete lifecycle of summaries from creation to archival.

```python
class SummaryStatus:
    STAGING = 0              # Initial AI-generated summary
    IN_PROGRESS = 1          # Being actively edited
    SUBMITTED = 2            # Final version ready for use
    ARCHIVED = 3             # Historical/inactive version
    SAVED_FOR_LATER = 4      # Draft saved for future work
    STAGED_FOR_SUBMIT = 5    # Ready for final submission
```

#### Status Lifecycle Flow

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   STAGING   │───▶│  IN_PROGRESS    │───▶│  SUBMITTED  │
│     (0)     │    │      (1)        │    │     (2)     │
└─────────────┘    └─────────────────┘    └─────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│STAGED_FOR_  │    │ SAVED_FOR_LATER │    │  ARCHIVED   │
│SUBMIT (5)   │    │      (4)        │    │     (3)     │
└─────────────┘    └─────────────────┘    └─────────────┘
```

#### Status Definitions and Usage

| Status | Value | Description | Typical Actions | Next States |
|--------|-------|-------------|-----------------|-------------|
| **STAGING** | 0 | Initial AI-generated summary for review | • Review content<br>• Edit via LLM<br>• Manual editing | IN_PROGRESS<br>STAGED_FOR_SUBMIT |
| **IN_PROGRESS** | 1 | Summary being actively edited | • Continue editing<br>• Add comments<br>• Collaborate | SUBMITTED<br>SAVED_FOR_LATER |
| **SUBMITTED** | 2 | Final version ready for use | • Share with stakeholders<br>• Export/publish<br>• Archive when done | ARCHIVED |
| **ARCHIVED** | 3 | Historical/inactive version | • View for reference<br>• Restore if needed | IN_PROGRESS (restore) |
| **SAVED_FOR_LATER** | 4 | Draft saved for future work | • Resume editing<br>• Delete if not needed | IN_PROGRESS<br>ARCHIVED |
| **STAGED_FOR_SUBMIT** | 5 | Ready for final submission | • Final review<br>• Submit for approval | SUBMITTED<br>IN_PROGRESS |

#### Usage Examples

```python
from app.models.constants import SummaryStatus

# In summary builder - set initial status
summary = Summary(
    summary_id=summary_id,
    content=llm_text,
    status_id=SummaryStatus.STAGING,  # Initial status
    effective_from=datetime.now(timezone.utc),
    created_by=action_by,
)

# Status transition logic
def can_transition_to(current_status: int, target_status: int) -> bool:
    valid_transitions = {
        SummaryStatus.STAGING: [
            SummaryStatus.IN_PROGRESS, 
            SummaryStatus.STAGED_FOR_SUBMIT
        ],
        SummaryStatus.IN_PROGRESS: [
            SummaryStatus.SUBMITTED, 
            SummaryStatus.SAVED_FOR_LATER
        ],
        SummaryStatus.SUBMITTED: [
            SummaryStatus.ARCHIVED
        ],
        SummaryStatus.SAVED_FOR_LATER: [
            SummaryStatus.IN_PROGRESS, 
            SummaryStatus.ARCHIVED
        ],
        SummaryStatus.STAGED_FOR_SUBMIT: [
            SummaryStatus.SUBMITTED, 
            SummaryStatus.IN_PROGRESS
        ]
    }
    
    return target_status in valid_transitions.get(current_status, [])

# Status-based filtering
def get_active_summaries_filter():
    return [
        SummaryStatus.STAGING,
        SummaryStatus.IN_PROGRESS,
        SummaryStatus.SUBMITTED,
        SummaryStatus.STAGED_FOR_SUBMIT
    ]

def get_draft_summaries_filter():
    return [
        SummaryStatus.STAGING,
        SummaryStatus.IN_PROGRESS,
        SummaryStatus.SAVED_FOR_LATER
    ]
```

#### Status-Based Business Logic

```python
# Determine available actions based on status
def get_available_actions(status_id: int, user_role: int) -> List[str]:
    actions = []
    
    if status_id == SummaryStatus.STAGING:
        actions.extend(['edit_via_llm', 'manual_edit', 'stage_for_submit'])
        if user_role in [Roles.OWNER, Roles.ADMIN]:
            actions.append('share')
    
    elif status_id == SummaryStatus.IN_PROGRESS:
        actions.extend(['edit', 'add_comment', 'save_for_later'])
        if user_role in [Roles.OWNER, Roles.EDITOR, Roles.ADMIN]:
            actions.append('submit')
    
    elif status_id == SummaryStatus.SUBMITTED:
        actions.extend(['view', 'add_comment', 'export'])
        if user_role in [Roles.OWNER, Roles.ADMIN]:
            actions.extend(['archive', 'share'])
    
    return actions

# Status validation
VALID_STATUSES = [
    SummaryStatus.STAGING,
    SummaryStatus.IN_PROGRESS,
    SummaryStatus.SUBMITTED,
    SummaryStatus.ARCHIVED,
    SummaryStatus.SAVED_FOR_LATER,
    SummaryStatus.STAGED_FOR_SUBMIT
]

def validate_status(status_id: int) -> bool:
    return status_id in VALID_STATUSES
```

## Entity Type Classification

### Entity Type IDs

The system uses entity type IDs to classify different types of records for auditing and reporting purposes.

```python
# Entity type constants (inferred from ORM models)
ENTITY_TYPES = {
    'USER': 0,           # User records
    'SUMMARY': 1,        # Summary records
    'COMMENT': 4,        # Comment records
    'USER_PROMPT': 5,    # User prompt records
}
```

#### Usage in ORM Models

```python
# In User model
entity_type_id: Mapped[Optional[int]] = mapped_column(
    BigInteger, default=0, nullable=False  # USER entity type
)

# In Summary model
entity_type_id: Mapped[Optional[int]] = mapped_column(
    BigInteger, default=1, nullable=False  # SUMMARY entity type
)

# In Comment model
entity_type_id: Mapped[Optional[int]] = mapped_column(
    BigInteger, default=4, nullable=False  # COMMENT entity type
)
```

## Configuration Constants

### Default Values

```python
# Default settings used throughout the application
DEFAULT_LLM_MODEL = "gemini/gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
DEFAULT_VECTOR_DIMENSION = 768

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Content limits
MAX_SUMMARY_LENGTH = 100000  # 100KB
MAX_COMMENT_LENGTH = 10000   # 10KB
MAX_PROMPT_LENGTH = 5000     # 5KB
```

### System Limits

```python
# Database constraints
MAX_USERNAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_NAME_LENGTH = 255

# File and content limits
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
MAX_BATCH_SIZE = 100  # Maximum items in bulk operations

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 60
MAX_LLM_REQUESTS_PER_HOUR = 100
```

## Validation Constants

### Regular Expressions

```python
import re

# Email validation pattern
EMAIL_PATTERN = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

# Username validation (alphanumeric, dots, underscores)
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9._]+$')

# UUID validation
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)
```

### Validation Rules

```python
# Field validation constants
MIN_PASSWORD_LENGTH = 8
MIN_SUMMARY_TITLE_LENGTH = 3
MAX_SUMMARY_TITLE_LENGTH = 200

# Content validation
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
]

FORBIDDEN_CONTENT_PATTERNS = [
    r'<script.*?>.*?</script>',  # No JavaScript
    r'<iframe.*?>.*?</iframe>',  # No iframes
    r'javascript:',              # No JavaScript URLs
]
```

## Error Constants

### HTTP Status Codes

```python
# Custom error codes for specific business logic
class ErrorCodes:
    # Authentication errors
    INVALID_TOKEN = 4001
    TOKEN_EXPIRED = 4002
    INSUFFICIENT_PERMISSIONS = 4003
    
    # Validation errors
    INVALID_EMAIL_FORMAT = 4221
    INVALID_UUID_FORMAT = 4222
    CONTENT_TOO_LONG = 4223
    
    # Business logic errors
    SUMMARY_NOT_FOUND = 4041
    COMMENT_NOT_FOUND = 4042
    USER_NOT_FOUND = 4043
    
    # State errors
    INVALID_STATUS_TRANSITION = 4091
    SUMMARY_ALREADY_SUBMITTED = 4092
    CANNOT_EDIT_ARCHIVED = 4093
```

### Error Messages

```python
ERROR_MESSAGES = {
    ErrorCodes.INVALID_TOKEN: "Invalid or malformed authentication token",
    ErrorCodes.TOKEN_EXPIRED: "Authentication token has expired",
    ErrorCodes.INSUFFICIENT_PERMISSIONS: "Insufficient permissions for this operation",
    
    ErrorCodes.INVALID_EMAIL_FORMAT: "Email address format is invalid",
    ErrorCodes.INVALID_UUID_FORMAT: "UUID format is invalid",
    ErrorCodes.CONTENT_TOO_LONG: "Content exceeds maximum allowed length",
    
    ErrorCodes.SUMMARY_NOT_FOUND: "Summary not found or access denied",
    ErrorCodes.COMMENT_NOT_FOUND: "Comment not found or access denied",
    ErrorCodes.USER_NOT_FOUND: "User not found or inactive",
    
    ErrorCodes.INVALID_STATUS_TRANSITION: "Invalid status transition requested",
    ErrorCodes.SUMMARY_ALREADY_SUBMITTED: "Summary has already been submitted",
    ErrorCodes.CANNOT_EDIT_ARCHIVED: "Cannot edit archived summary",
}
```

## Usage Patterns

### 1. Constant Import and Usage

```python
# Import constants at module level
from app.models.constants import Roles, SummaryStatus

# Use in business logic
def assign_default_role(user_id: UUID, summary_id: UUID):
    return SummariesUsersCreateRequest(
        summary_id=summary_id,
        user_id=user_id,
        role_id=Roles.OWNER  # Use constant instead of magic number
    )

def create_staging_summary(content: str):
    return Summary(
        content=content,
        status_id=SummaryStatus.STAGING  # Clear intent
    )
```

### 2. Validation with Constants

```python
def validate_role_assignment(role_id: int) -> bool:
    """Validate that role_id is a valid role constant."""
    valid_roles = [Roles.OWNER, Roles.EDITOR, Roles.VIEWER, Roles.ADMIN]
    return role_id in valid_roles

def validate_status_transition(from_status: int, to_status: int) -> bool:
    """Validate that status transition is allowed."""
    if from_status == SummaryStatus.STAGING:
        return to_status in [SummaryStatus.IN_PROGRESS, SummaryStatus.STAGED_FOR_SUBMIT]
    elif from_status == SummaryStatus.IN_PROGRESS:
        return to_status in [SummaryStatus.SUBMITTED, SummaryStatus.SAVED_FOR_LATER]
    # ... more transition rules
    return False
```

### 3. API Documentation with Constants

```python
from enum import IntEnum

class RoleEnum(IntEnum):
    """User role enumeration for API documentation."""
    OWNER = Roles.OWNER
    EDITOR = Roles.EDITOR
    VIEWER = Roles.VIEWER
    ADMIN = Roles.ADMIN

class StatusEnum(IntEnum):
    """Summary status enumeration for API documentation."""
    STAGING = SummaryStatus.STAGING
    IN_PROGRESS = SummaryStatus.IN_PROGRESS
    SUBMITTED = SummaryStatus.SUBMITTED
    ARCHIVED = SummaryStatus.ARCHIVED
    SAVED_FOR_LATER = SummaryStatus.SAVED_FOR_LATER
    STAGED_FOR_SUBMIT = SummaryStatus.STAGED_FOR_SUBMIT
```

## Best Practices

### 1. Constant Definition
- Use descriptive class names for grouping related constants
- Use ALL_CAPS for constant names within classes
- Provide clear numeric values that reflect hierarchy or sequence
- Document the meaning and usage of each constant

### 2. Constant Usage
- Always import and use constants instead of magic numbers
- Use constants in validation functions and business logic
- Create helper functions for common constant-based operations
- Validate constant values at runtime when accepting user input

### 3. Maintenance
- Keep constants centralized in the constants module
- Update all usages when changing constant values
- Use constants in database migrations and seed data
- Document any changes to constant values and their impact

### 4. Testing
- Test all constant-based validation logic
- Verify that all valid constant values are accepted
- Test edge cases and invalid constant values
- Include constants in integration tests for API endpoints

### 5. Documentation
- Document the business meaning of each constant
- Provide examples of how constants are used
- Explain any relationships or hierarchies between constants
- Keep API documentation synchronized with constant definitions