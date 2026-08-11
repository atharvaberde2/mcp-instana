"""
Unit tests for CustomDashboardSmartRouterMCPTool
"""

import asyncio
import logging
import os
import sys
import unittest
from functools import wraps
from unittest.mock import AsyncMock, MagicMock, patch


# Create a null handler that will discard all log messages
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


# Configure root logger to use ERROR level
logging.basicConfig(level=logging.ERROR)

# Get the router logger and replace its handlers
router_logger = logging.getLogger('src.router.custom_dashboard_smart_router_tool')
router_logger.handlers = []
router_logger.addHandler(NullHandler())
router_logger.propagate = False

# Add src to path before any imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Create a mock for the with_header_auth decorator
def mock_with_header_auth(api_class, allow_mock=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


# Patch the with_header_auth decorator and the client imports
with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    # Mock the client class at its import location
    with patch('src.custom_dashboard.custom_dashboard_tools.CustomDashboardMCPTools') as MockDashboard:

        # Import the router class
        from src.router.custom_dashboard_smart_router_tool import (
            CustomDashboardSmartRouterMCPTool,
        )


class TestCustomDashboardSmartRouterMCPTool(unittest.TestCase):
    """Test class for CustomDashboardSmartRouterMCPTool"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock instance for dashboard client
        self.mock_dashboard = MagicMock()

        # Patch the client class at import time
        with patch('src.custom_dashboard.custom_dashboard_tools.CustomDashboardMCPTools', return_value=self.mock_dashboard):

            # Create router instance
            self.router = CustomDashboardSmartRouterMCPTool(
                read_token="test_token",
                base_url="https://test.instana.com"
            )

            # Manually set the client on the router
            self.router.dashboard_client = self.mock_dashboard

    def test_init(self):
        """Test router initialization"""
        self.assertEqual(self.router.read_token, "test_token")
        self.assertEqual(self.router.base_url, "https://test.instana.com")
        self.assertIsNotNone(self.router.dashboard_client)

    def test_invalid_operation(self):
        """Test handling of invalid operation"""
        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="invalid_op"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("invalid_op", (result.get("error") or result.get("message", "")).lower())

    def test_get_all_dashboards(self):
        """Test get_all operation"""
        async def mock_execute(*args, **kwargs):
            return {"dashboards": []}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get_all",
            params={"page_size": 20}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["operation"], "get_all")

    def test_get_dashboard_by_id(self):
        """Test get operation"""
        async def mock_execute(*args, **kwargs):
            return {"id": "dash-123", "title": "Test Dashboard"}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get",
            params={"dashboard_id": "dash-123"}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["dashboard_id"], "dash-123")

    def test_create_dashboard(self):
        """Test create operation"""
        async def mock_execute(*args, **kwargs):
            return {"id": "new-dash", "title": "New Dashboard"}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="create",
            params={
                "custom_dashboard": {
                    "title": "New Dashboard",
                    "accessRules": [{"accessType": "READ_WRITE", "relationType": "GLOBAL"}],
                    "widgets": []
                }
            }
        ))

        self.assertIn("results", result)

    def test_update_dashboard(self):
        """Test update operation"""
        async def mock_execute(*args, **kwargs):
            return {"id": "dash-123", "title": "Updated Dashboard"}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="update",
            params={
                "dashboard_id": "dash-123",
                "custom_dashboard": {
                    "title": "Updated Dashboard",
                    "accessRules": [{"accessType": "READ_WRITE", "relationType": "GLOBAL"}],
                    "widgets": []
                }
            }
        ))

        self.assertIn("results", result)
        self.assertEqual(result["dashboard_id"], "dash-123")

    def test_delete_dashboard(self):
        """Test delete operation"""
        async def mock_execute(*args, **kwargs):
            return {"success": True}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="delete",
            params={"dashboard_id": "dash-123"}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["dashboard_id"], "dash-123")

    def test_get_shareable_users(self):
        """Test get_shareable_users operation"""
        async def mock_execute(*args, **kwargs):
            return {"users": []}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get_shareable_users"
        ))

        self.assertIn("results", result)

    def test_get_shareable_api_tokens(self):
        """Test get_shareable_api_tokens operation"""
        async def mock_execute(*args, **kwargs):
            return {"tokens": []}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get_shareable_api_tokens"
        ))

        self.assertIn("results", result)

    def test_exception_handling(self):
        """Test exception handling in router"""
        async def mock_error(*args, **kwargs):
            raise Exception("Test error")

        self.mock_dashboard.execute_dashboard_operation = mock_error

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get_all"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("Test error", str((result.get("error") or result.get("message", ""))))

    def test_params_none_handling(self):
        """Test handling when params is None"""
        async def mock_execute(*args, **kwargs):
            return {"dashboards": []}

        self.mock_dashboard.execute_dashboard_operation = mock_execute

        result = asyncio.run(self.router.manage_custom_dashboards(
            operation="get_all",
            params=None
        ))

        self.assertIn("results", result)


if __name__ == '__main__':
    unittest.main()
