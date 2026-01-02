# Requirements Document

## Introduction

This feature integrates the existing TaskDTO and SaaranshResponseDTO models from nirdesh_dto_model.py into the NirdeshIntegration class to provide proper data validation and structured responses while returning dictionary objects for API consumers.

## Glossary

- **TaskDTO**: An existing Pydantic model in nirdesh_dto_model.py with id, title, description, and status fields
- **SaaranshResponseDTO**: An existing Pydantic model in nirdesh_dto_model.py containing a list of TaskDTO objects
- **NirdeshIntegration**: The service class that needs to be updated to use the existing DTO models
- **Dictionary Response**: JSON-serializable dictionary objects returned by API methods after DTO validation

## Requirements

### Requirement 1

**User Story:** As a developer consuming the Nirdesh integration API, I want the existing TaskDTO models to be integrated into the get_tasks method to validate responses and return dictionaries, so that I get structured, validated data in a flexible format.

#### Acceptance Criteria

1. WHEN the get_tasks method receives a response, THE NirdeshIntegration SHALL parse it using SaaranshResponseDTO from nirdesh_dto_model
2. WHEN SaaranshResponseDTO validation succeeds, THE NirdeshIntegration SHALL convert the Tasks list to dictionaries using model_dump()
3. WHEN the response contains task data, THE NirdeshIntegration SHALL return List[dict] with TaskDTO structure
4. WHEN the response is empty or None, THE NirdeshIntegration SHALL return None or empty list as appropriate
5. IF response validation fails, THEN THE NirdeshIntegration SHALL raise ValidationError with detailed information

### Requirement 2

**User Story:** As a system architect, I want to import and use the existing DTO models from nirdesh_dto_model.py, so that we maintain consistency across the codebase and leverage existing data structures.

#### Acceptance Criteria

1. WHEN NirdeshIntegration is updated, THE class SHALL import TaskDTO and SaaranshResponseDTO from app.models.nirdesh_dto_model
2. WHEN processing task responses, THE NirdeshIntegration SHALL use SaaranshResponseDTO for validation
3. WHEN converting to dictionaries, THE NirdeshIntegration SHALL use the model_dump() method from validated DTO instances
4. WHILE maintaining existing functionality, THE NirdeshIntegration SHALL preserve current method signatures and return types
5. WHERE validation errors occur, THE NirdeshIntegration SHALL provide meaningful error messages

### Requirement 3

**User Story:** As an API consumer, I want consistent dictionary responses from all task-related methods, so that I can handle responses uniformly across the application.

#### Acceptance Criteria

1. WHEN get_tasks method returns data, THE NirdeshIntegration SHALL return List[dict] or None
2. WHEN get_user_data_for_report includes task data, THE NirdeshIntegration SHALL include tasks as dictionary objects
3. WHEN task data is processed in any method, THE NirdeshIntegration SHALL ensure consistent dictionary structure
4. WHILE processing task responses, THE NirdeshIntegration SHALL maintain all original task fields in dictionary format
5. WHERE multiple tasks are returned, THE NirdeshIntegration SHALL return them as a list of dictionaries