# Implementation Plan

- [x] 1. Add DTO model imports to NirdeshIntegration


  - Import TaskDTO and SaaranshResponseDTO from app.models.nirdesh_dto_model
  - Import ValidationError from pydantic for error handling
  - _Requirements: 2.1_





- [ ] 2. Enhance get_tasks method with DTO validation
  - [x] 2.1 Add response validation using SaaranshResponseDTO

    - Parse JSON response using SaaranshResponseDTO model
    - Handle validation errors with meaningful error messages
    - _Requirements: 1.1, 1.5_
  

  - [ ] 2.2 Convert validated TaskDTO objects to dictionaries
    - Use model_dump() method to convert TaskDTO instances to dictionaries
    - Return List[dict] with TaskDTO structure
    - _Requirements: 1.2, 1.3_




  
  - [ ] 2.3 Preserve existing error handling patterns
    - Maintain 204 status code handling (return None)

    - Preserve HTTP error raising behavior
    - Handle empty tasks list scenarios
    - _Requirements: 1.4, 2.4_






- [ ] 3. Update get_user_data_for_report method
  - [x] 3.1 Integrate enhanced get_tasks method


    - Use the updated get_tasks method that returns validated dictionaries
    - Ensure task data in report response uses validated structure
    - _Requirements: 3.2, 3.3_
  
  - [ ] 3.2 Maintain existing response structure
    - Preserve current response format for backward compatibility
    - Ensure tasks field contains dictionary objects
    - _Requirements: 3.4, 2.4_

- [ ] 4. Add comprehensive error handling tests
  - [ ] 4.1 Test validation error scenarios
    - Create tests for malformed API responses
    - Verify ValidationError handling and error messages
    - _Requirements: 1.5, 2.5_
  
  - [ ] 4.2 Test successful validation and conversion
    - Test valid API response processing
    - Verify dictionary structure matches TaskDTO fields
    - Test empty response scenarios
    - _Requirements: 1.1, 1.2, 1.3_