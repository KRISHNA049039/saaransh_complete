from typing import Optional, List
from app.models.request.users_request import UserFetchFilter
from app.models.nirdesh_dto_model import TaskDTO, SaaranshResponseDTO
from app.config.security.oauth2_client import m2m_oauth2_client
from app.settings import settings
from pydantic import ValidationError


class NirdeshIntegration:

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.NIRDESH_DB_SERVICE_URL).rstrip("/")
        self.client = m2m_oauth2_client

    async def get_tasks(
        self,
        user_email: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[dict]]:

        params = {"userEmail": user_email}

        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = await self.client.get(
            f"{self.base_url}/api/tasks",
            params=params
        )

        if response.status_code == 204:
            return None

        response.raise_for_status()
        
        try:
            # Parse and validate response using SaaranshResponseDTO
            response_data = response.json()
            validated_response = SaaranshResponseDTO(**response_data)
            
            # Convert TaskDTO objects to dictionaries
            return [task.model_dump() for task in validated_response.Tasks]
            
        except ValidationError as e:
            raise ValidationError(f"Invalid task response structure from Nirdesh API: {str(e)}")
        except Exception as e:
            # Handle cases where response is not valid JSON or other parsing errors
            raise ValueError(f"Failed to parse task response from Nirdesh API: {str(e)}")

    async def get_users(self, filters: Optional[UserFetchFilter] = None) -> List[dict]:
        """Get users from Nirdesh with optional filtering"""
        params = {}
        
        if filters:
            # Convert UserFetchFilter to query parameters
            filter_dict = filters.model_dump(exclude_none=True)
            for key, value in filter_dict.items():
                if key != "effective_only":  # Skip SCD2 filter field
                    params[key] = value

        response = await self.client.get(
            f"{self.base_url}/api/users",
            params=params if params else None
        )

        if response.status_code == 204:
            return []

        response.raise_for_status()
        return response.json()

    async def m2m_check(self) -> dict:
        """Check M2M authentication with Nirdesh service - similar to auth_test_handler"""
        try:
            response = await self.client.get(f"{self.base_url}/api/users/m2m")
            token_info = self.client.get_token_details()

            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
            else:
                data = response.text
                
            return {
                "message": "M2M client credentials flow is working with Nirdesh!",
                "token_expires_in": token_info.get("expires_in") if token_info else None,
                "token_expires_at": token_info.get("expires_at") if token_info else None,
                "token_type": token_info.get("token_type") if token_info else None,
                "response": data,
                "response_status": response.status_code,
                "response_headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "message": "M2M check failed",
                "error": str(e),
                "response_status": None
            }

    async def health_check(self) -> bool:
        """Check if Nirdesh service is accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except Exception:
            return False

    async def get_user_data_for_report(self, user_email: str) -> dict:
        """Get comprehensive user data for reports"""
        try:
            # Get tasks for the user (now returns List[dict] or None)
            tasks_data = await self.get_tasks(user_email)
            
            # Get user info if available
            user_filter = UserFetchFilter(user_email=user_email)
            users = await self.get_users(user_filter)
            user_info = users[0] if users else None
            
            return {
                "user_email": user_email,
                "user": user_info if user_info else None,
                "tasks": tasks_data if tasks_data else None,
                "total_tasks": len(tasks_data) if tasks_data else 0,
                "source": "nirdesh"
            }
        except Exception as e:
            return {
                "user_email": user_email,
                "error": str(e),
                "tasks": None,
                "total_tasks": 0,
                "source": "nirdesh"
            }
