import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import ValidationError
from app.accessors.integrations.nirdesh_integration import NirdeshIntegration
from app.models.nirdesh_dto_model import TaskDTO, SaaranshResponseDTO


class TestNirdeshIntegration:
    
    @pytest.fixture
    def nirdesh_integration(self):
        """Create a NirdeshIntegration instance for testing"""
        return NirdeshIntegration(base_url="http://test-nirdesh.com")
    
    @pytest.fixture
    def mock_client(self, nirdesh_integration):
        """Mock the OAuth2 client"""
        mock_client = AsyncMock()
        nirdesh_integration.client = mock_client
        return mock_client

    @pytest.mark.asyncio
    async def test_get_tasks_validation_error_malformed_response(self, nirdesh_integration, mock_client):
        """Test validation error handling with malformed API response"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "InvalidField": "invalid_data"  # Missing required "Tasks" field
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await nirdesh_integration.get_tasks("test@example.com")
        
        assert "Invalid task response structure from Nirdesh API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_tasks_validation_error_invalid_task_structure(self, nirdesh_integration, mock_client):
        """Test validation error with invalid task structure"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Tasks": [
                {
                    # Missing required "id" field
                    "title": "Test Task",
                    "description": "Test Description"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await nirdesh_integration.get_tasks("test@example.com")
        
        assert "Invalid task response structure from Nirdesh API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_tasks_json_parsing_error(self, nirdesh_integration, mock_client):
        """Test error handling when response is not valid JSON"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await nirdesh_integration.get_tasks("test@example.com")
        
        assert "Failed to parse task response from Nirdesh API" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_tasks_successful_validation_and_conversion(self, nirdesh_integration, mock_client):
        """Test successful API response processing and dictionary conversion"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Tasks": [
                {
                    "id": "task_123",
                    "title": "Test Task 1",
                    "description": "Test Description 1",
                    "status": "active"
                },
                {
                    "id": "task_456",
                    "title": "Test Task 2",
                    "description": "Test Description 2",
                    "status": "completed"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act
        result = await nirdesh_integration.get_tasks("test@example.com")
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Verify first task structure
        assert result[0] == {
            "id": "task_123",
            "title": "Test Task 1",
            "description": "Test Description 1",
            "status": "active"
        }
        
        # Verify second task structure
        assert result[1] == {
            "id": "task_456",
            "title": "Test Task 2",
            "description": "Test Description 2",
            "status": "completed"
        }

    @pytest.mark.asyncio
    async def test_get_tasks_empty_tasks_list(self, nirdesh_integration, mock_client):
        """Test handling of empty tasks list"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Tasks": []
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act
        result = await nirdesh_integration.get_tasks("test@example.com")
        
        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_tasks_204_response(self, nirdesh_integration, mock_client):
        """Test handling of 204 No Content response"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_client.get.return_value = mock_response
        
        # Act
        result = await nirdesh_integration.get_tasks("test@example.com")
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_tasks_with_optional_fields_none(self, nirdesh_integration, mock_client):
        """Test successful processing with optional fields as None"""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Tasks": [
                {
                    "id": "task_789",
                    "title": None,
                    "description": None,
                    "status": None
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Act
        result = await nirdesh_integration.get_tasks("test@example.com")
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == {
            "id": "task_789",
            "title": None,
            "description": None,
            "status": None
        }

    @pytest.mark.asyncio
    async def test_get_user_data_for_report_with_tasks(self, nirdesh_integration, mock_client):
        """Test get_user_data_for_report with successful task data"""
        # Arrange
        # Mock get_tasks response
        mock_tasks_response = MagicMock()
        mock_tasks_response.status_code = 200
        mock_tasks_response.json.return_value = {
            "Tasks": [
                {
                    "id": "task_123",
                    "title": "Report Task",
                    "description": "Task for report",
                    "status": "active"
                }
            ]
        }
        mock_tasks_response.raise_for_status.return_value = None
        
        # Mock get_users response
        mock_users_response = MagicMock()
        mock_users_response.status_code = 200
        mock_users_response.json.return_value = [
            {
                "email": "test@example.com",
                "name": "Test User"
            }
        ]
        mock_users_response.raise_for_status.return_value = None
        
        # Configure mock client to return different responses for different endpoints
        def mock_get(url, **kwargs):
            if "/api/tasks" in url:
                return mock_tasks_response
            elif "/api/users" in url:
                return mock_users_response
        
        mock_client.get.side_effect = mock_get
        
        # Act
        result = await nirdesh_integration.get_user_data_for_report("test@example.com")
        
        # Assert
        assert result["user_email"] == "test@example.com"
        assert result["user"] == {"email": "test@example.com", "name": "Test User"}
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["id"] == "task_123"
        assert result["total_tasks"] == 1
        assert result["source"] == "nirdesh"

    @pytest.mark.asyncio
    async def test_get_user_data_for_report_no_tasks(self, nirdesh_integration, mock_client):
        """Test get_user_data_for_report when no tasks are returned"""
        # Arrange
        # Mock get_tasks response (204 No Content)
        mock_tasks_response = MagicMock()
        mock_tasks_response.status_code = 204
        
        # Mock get_users response
        mock_users_response = MagicMock()
        mock_users_response.status_code = 200
        mock_users_response.json.return_value = [
            {
                "email": "test@example.com",
                "name": "Test User"
            }
        ]
        mock_users_response.raise_for_status.return_value = None
        
        def mock_get(url, **kwargs):
            if "/api/tasks" in url:
                return mock_tasks_response
            elif "/api/users" in url:
                return mock_users_response
        
        mock_client.get.side_effect = mock_get
        
        # Act
        result = await nirdesh_integration.get_user_data_for_report("test@example.com")
        
        # Assert
        assert result["user_email"] == "test@example.com"
        assert result["user"] == {"email": "test@example.com", "name": "Test User"}
        assert result["tasks"] is None
        assert result["total_tasks"] == 0
        assert result["source"] == "nirdesh"

    @pytest.mark.asyncio
    async def test_get_user_data_for_report_error_handling(self, nirdesh_integration, mock_client):
        """Test get_user_data_for_report error handling"""
        # Arrange
        mock_client.get.side_effect = Exception("Network error")
        
        # Act
        result = await nirdesh_integration.get_user_data_for_report("test@example.com")
        
        # Assert
        assert result["user_email"] == "test@example.com"
        assert "error" in result
        assert "Network error" in result["error"]
        assert result["tasks"] is None
        assert result["total_tasks"] == 0
        assert result["source"] == "nirdesh"

    @pytest.mark.asyncio
    async def test_get_user_data_for_report_validation_error_propagation(self, nirdesh_integration, mock_client):
        """Test that validation errors from get_tasks are properly handled in get_user_data_for_report"""
        # Arrange
        # Mock get_tasks to return invalid response
        mock_tasks_response = MagicMock()
        mock_tasks_response.status_code = 200
        mock_tasks_response.json.return_value = {
            "InvalidField": "invalid_data"  # Missing required "Tasks" field
        }
        mock_tasks_response.raise_for_status.return_value = None
        
        # Mock get_users response
        mock_users_response = MagicMock()
        mock_users_response.status_code = 200
        mock_users_response.json.return_value = []
        mock_users_response.raise_for_status.return_value = None
        
        def mock_get(url, **kwargs):
            if "/api/tasks" in url:
                return mock_tasks_response
            elif "/api/users" in url:
                return mock_users_response
        
        mock_client.get.side_effect = mock_get
        
        # Act
        result = await nirdesh_integration.get_user_data_for_report("test@example.com")
        
        # Assert
        assert result["user_email"] == "test@example.com"
        assert "error" in result
        assert "Invalid task response structure from Nirdesh API" in result["error"]
        assert result["tasks"] is None
        assert result["total_tasks"] == 0
        assert result["source"] == "nirdesh"