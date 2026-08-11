"""
Unit tests for AutomationSmartRouterMCPTool
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
router_logger = logging.getLogger('src.router.automation_smart_router_tool')
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


# Pre-load the automation modules so patch() can find their attributes
import src.automation.action_catalog
import src.automation.action_history

# Patch the with_header_auth decorator and the client imports
with patch('src.core.utils.with_header_auth', mock_with_header_auth):
    # Mock the client classes at their import location
    with patch('src.automation.action_catalog.ActionCatalogMCPTools') as MockCatalog, \
         patch('src.automation.action_history.ActionHistoryMCPTools') as MockHistory:

        # Import the router class
        from src.router.automation_smart_router_tool import AutomationSmartRouterMCPTool


class TestAutomationSmartRouterMCPTool(unittest.TestCase):
    """Test class for AutomationSmartRouterMCPTool"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock instances for all clients
        self.mock_catalog = MagicMock()
        self.mock_history = MagicMock()

        # Patch the client classes at import time
        with patch('src.automation.action_catalog.ActionCatalogMCPTools', return_value=self.mock_catalog), \
             patch('src.automation.action_history.ActionHistoryMCPTools', return_value=self.mock_history):

            # Create router instance
            self.router = AutomationSmartRouterMCPTool(
                read_token="test_token",
                base_url="https://test.instana.com"
            )

            # Manually set the clients on the router
            self.router.action_catalog_client = self.mock_catalog
            self.router.action_history_client = self.mock_history

    def test_init(self):
        """Test router initialization"""
        self.assertEqual(self.router.read_token, "test_token")
        self.assertEqual(self.router.base_url, "https://test.instana.com")
        self.assertIsNotNone(self.router.action_catalog_client)
        self.assertIsNotNone(self.router.action_history_client)

    def test_invalid_resource_type(self):
        """Test handling of invalid resource type"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="invalid_type",
            operation="test"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("invalid_type", (result.get("error") or result.get("message", "")).lower())

    def test_invalid_catalog_operation(self):
        """Test invalid operation for catalog resource type"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="invalid_op"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("invalid_op", (result.get("error") or result.get("message", "")).lower())

    def test_get_actions(self):
        """Test get_actions operation"""
        async def mock_get_actions(*args, **kwargs):
            return {"actions": []}

        self.mock_catalog.get_actions = mock_get_actions

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_actions"
        ))

        self.assertIn("results", result)
        self.assertEqual(result["resource_type"], "catalog")

    def test_get_action_details(self):
        """Test get_action_details operation"""
        async def mock_get_details(*args, **kwargs):
            return {"action": "details"}

        self.mock_catalog.get_action_details = mock_get_details

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_details",
            params={"action_id": "action-123"}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["action_id"], "action-123")

    def test_get_action_details_missing_id(self):
        """Test get_action_details without action_id"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_details"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("action_id", (result.get("error") or result.get("message", "")).lower())

    def test_get_action_matches(self):
        """Test get_action_matches operation"""
        async def mock_get_matches(*args, **kwargs):
            return {"matches": []}

        self.mock_catalog.get_action_matches = mock_get_matches

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_matches",
            params={"payload": {"name": "CPU", "description": "monitoring"}}
        ))

        self.assertIn("results", result)

    def test_get_action_matches_missing_payload(self):
        """Test get_action_matches without payload"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_matches"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("payload", (result.get("error") or result.get("message", "")).lower())

    def test_get_action_matches_by_id(self):
        """Test get_action_matches_by_id_and_time_window operation"""
        async def mock_get_matches(*args, **kwargs):
            return {"matches": []}

        self.mock_catalog.get_action_matches_by_id_and_time_window = mock_get_matches

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_matches_by_id_and_time_window",
            params={"application_id": "app-123", "window_size": 3600000}
        ))

        self.assertIn("results", result)

    def test_get_action_matches_by_id_missing_ids(self):
        """Test get_action_matches_by_id without required IDs"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_matches_by_id_and_time_window"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))

    def test_get_action_types(self):
        """Test get_action_types operation"""
        async def mock_get_types(*args, **kwargs):
            return {"types": []}

        self.mock_catalog.get_action_types = mock_get_types

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_types"
        ))

        self.assertIn("results", result)

    def test_get_action_tags(self):
        """Test get_action_tags operation"""
        async def mock_get_tags(*args, **kwargs):
            return {"tags": []}

        self.mock_catalog.get_action_tags = mock_get_tags

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_action_tags"
        ))

        self.assertIn("results", result)

    def test_list_action_instances(self):
        """Test list operation for history"""
        async def mock_list(*args, **kwargs):
            return {"instances": []}

        self.mock_history.list_action_instances = mock_list

        result = asyncio.run(self.router.manage_automation(
            resource_type="history",
            operation="list",
            params={"window_size": 3600000, "page_size": 50}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["resource_type"], "history")

    def test_get_action_instance_details(self):
        """Test get_details operation for history"""
        async def mock_get_details(*args, **kwargs):
            return {"instance": "details"}

        self.mock_history.get_action_instance_details = mock_get_details

        result = asyncio.run(self.router.manage_automation(
            resource_type="history",
            operation="get_details",
            params={"action_instance_id": "instance-123"}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["action_instance_id"], "instance-123")

    def test_get_details_missing_id(self):
        """Test get_details without action_instance_id"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="history",
            operation="get_details"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("action_instance_id", (result.get("error") or result.get("message", "")).lower())

    def test_invalid_history_operation(self):
        """Test invalid operation for history resource type"""
        result = asyncio.run(self.router.manage_automation(
            resource_type="history",
            operation="invalid_op"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("invalid_op", (result.get("error") or result.get("message", "")).lower())

    def test_catalog_exception_handling(self):
        """Test exception handling in catalog operations"""
        async def mock_error(*args, **kwargs):
            raise Exception("Test error")

        self.mock_catalog.get_actions = mock_error

        result = asyncio.run(self.router.manage_automation(
            resource_type="catalog",
            operation="get_actions"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("Test error", str((result.get("error") or result.get("message", ""))))

    def test_history_exception_handling(self):
        """Test exception handling in history operations"""
        async def mock_error(*args, **kwargs):
            raise Exception("Test error")

        self.mock_history.list_action_instances = mock_error

        result = asyncio.run(self.router.manage_automation(
            resource_type="history",
            operation="list"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("Test error", str((result.get("error") or result.get("message", ""))))


if __name__ == '__main__':
    unittest.main()

