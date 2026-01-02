"""Test configuration for pytest"""
import pytest
import os
from unittest.mock import patch

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables to prevent configuration errors during testing"""
    with patch.dict(os.environ, {
        'DB_POOL_SIZE': '10',
        'NIRDESH_DB_SERVICE_URL': 'http://test-nirdesh.com',
        'KEYCLOAK_SERVER_URL': 'http://test-keycloak.com',
        'KEYCLOAK_REALM': 'test-realm',
        'KEYCLOAK_CLIENT_ID': 'test-client',
        'KEYCLOAK_CLIENT_SECRET': 'test-secret',
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'EMBEDDING_MODEL': 'text-embedding-ada-002',
        'VECTOR_DB_URL': 'http://test-vector-db.com',
        'VECTOR_DB_API_KEY': 'test-vector-key'
    }):
        yield