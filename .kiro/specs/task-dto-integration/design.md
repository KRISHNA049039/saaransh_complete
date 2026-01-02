# Design Document

## Overview

This design integrates the existing TaskDTO and SaaranshResponseDTO models from `app.models.nirdesh_dto_model` into the NirdeshIntegration class. The integration will provide data validation using Pydantic models while returning dictionary objects for API consumers, ensuring type safety during processing and flexibility in response handling.

## Architecture

### Current State
- TaskDTO and SaaranshResponseDTO models exist in `app.models.nirdesh_dto_model`
- NirdeshIntegration class in `app.accessors.integrations.nirdesh_integration` returns raw dictionary responses
- No validation is performed on external API responses

### Target State
- NirdeshIntegration imports and uses existing DTO models for validation
- Responses are validated using SaaranshResponseDTO before being returned as dictionaries
- Type safety is maintained during processing while preserving dictionary return types

## Components and Interfaces

### Modified Components

#### NirdeshIntegration Class
**Location:** `app/accessors/integrations/nirdesh_integration.py`

**New Imports:**
```python
from app.models.nirdesh_dto_model import TaskDTO, SaaranshResponseDTO
from pydantic import ValidationError
```

**Modified Methods:**

1. **get_tasks()** - Enhanced with DTO validation
   - Input: user_email, optional start_date, end_date
   - Processing: Validate response using SaaranshResponseDTO
   - Output: List[dict] or None (TaskDTO structure as dictionaries)

2. **get_user_data_for_report()** - Updated to use validated task data
   - Uses the enhanced get_tasks() method
   - Returns task data as dictionaries in the response structure

### Data Flow

```
External API Response → SaaranshResponseDTO Validation → TaskDTO List → Dictionary Conversion → Return List[dict]
```

## Data Models

### Existing Models (No Changes Required)

#### TaskDTO
```python
class TaskDTO(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
```

#### SaaranshResponseDTO
```python
class SaaranshResponseDTO(BaseModel):
    Tasks: List[TaskDTO]
```

### Response Structure

**get_tasks() Return Format:**
```python
# When tasks exist
[
    {
        "id": "task_123",
        "title": "Sample Task",
        "description": "Task description",
        "status": "active"
    },
    # ... more tasks
]

# When no tasks
None  # for 204 responses
[]    # for empty task lists
```

## Error Handling

### Validation Errors
- **Trigger:** Invalid response structure from external API
- **Handling:** Catch ValidationError and re-raise with context
- **Response:** Detailed error message indicating validation failure

### HTTP Errors
- **Existing:** Current HTTP error handling preserved
- **Enhancement:** Add validation context to error messages

### Empty Responses
- **204 Status:** Return None (existing behavior)
- **Empty Tasks List:** Return empty list after validation

## Testing Strategy

### Unit Tests
- Test successful response validation and dictionary conversion
- Test validation error handling with malformed responses
- Test empty response scenarios (204, empty tasks list)
- Test backward compatibility with existing method signatures

### Integration Tests
- Test end-to-end flow with actual Nirdesh API responses
- Verify dictionary structure matches TaskDTO model fields
- Test error propagation in get_user_data_for_report method

## Implementation Approach

### Phase 1: Import and Basic Integration
1. Add imports for TaskDTO and SaaranshResponseDTO
2. Add ValidationError import for error handling

### Phase 2: Enhance get_tasks Method
1. Add response validation using SaaranshResponseDTO
2. Convert validated TaskDTO objects to dictionaries
3. Preserve existing error handling and return patterns

### Phase 3: Update Dependent Methods
1. Update get_user_data_for_report to use enhanced get_tasks
2. Ensure all task-related data flows through DTO validation

### Phase 4: Error Handling Enhancement
1. Add meaningful error messages for validation failures
2. Ensure backward compatibility with existing error patterns

## Backward Compatibility

- Method signatures remain unchanged
- Return types remain as dictionaries
- Existing error handling patterns preserved
- No breaking changes to API consumers

## Performance Considerations

- Minimal overhead from Pydantic validation
- Dictionary conversion using model_dump() is efficient
- No additional network calls or processing delays
- Validation provides early error detection