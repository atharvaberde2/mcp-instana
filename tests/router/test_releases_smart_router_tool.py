"""
Unit tests for ReleasesSmartRouterMCPTool
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
router_logger = logging.getLogger('src.router.releases_smart_router_tool')
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
    with patch('src.releases.releases_tools.ReleasesMCPTools') as MockReleases:

        # Import the router class
        from src.router.releases_smart_router_tool import ReleasesSmartRouterMCPTool


class TestReleasesSmartRouterMCPTool(unittest.TestCase):
    """Test class for ReleasesSmartRouterMCPTool"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock instance for releases client
        self.mock_releases = MagicMock()

        # Patch the client class at import time
        with patch('src.releases.releases_tools.ReleasesMCPTools', return_value=self.mock_releases):

            # Create router instance
            self.router = ReleasesSmartRouterMCPTool(
                read_token="test_token",
                base_url="https://test.instana.com"
            )

            # Manually set the client on the router
            self.router.releases_client = self.mock_releases

    def test_init(self):
        """Test router initialization"""
        self.assertEqual(self.router.read_token, "test_token")
        self.assertEqual(self.router.base_url, "https://test.instana.com")
        self.assertIsNotNone(self.router.releases_client)

    def test_invalid_operation(self):
        """Test handling of invalid operation"""
        result = asyncio.run(self.router.manage_releases(
            operation="invalid_op"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("invalid_op", (result.get("error") or result.get("message", "")).lower())

    def test_get_all_releases(self):
        """Test get_all_releases operation"""
        async def mock_get_all(*args, **kwargs):
            return {"releases": []}

        self.mock_releases.get_all_releases = mock_get_all

        result = asyncio.run(self.router.manage_releases(
            operation="get_all_releases"
        ))

        self.assertIn("results", result)
        self.assertEqual(result["operation"], "get_all_releases")

    def test_get_all_releases_with_filters(self):
        """Test get_all_releases with filters"""
        async def mock_get_all(*args, **kwargs):
            return {"releases": []}

        self.mock_releases.get_all_releases = mock_get_all

        # Use valid timestamps (after Jan 1, 2020)
        result = asyncio.run(self.router.manage_releases(
            operation="get_all_releases",
            params={
                "from_time": 1700000000000,  # Nov 2023
                "to_time": 1700100000000,
                "name_filter": "frontend",
                "page_number": 1,
                "page_size": 50
            }
        ))

        self.assertIn("results", result)

    def test_get_release(self):
        """Test get_release operation"""
        async def mock_get(*args, **kwargs):
            return {"id": "release-123", "name": "frontend/release-2000"}

        self.mock_releases.get_release = mock_get

        result = asyncio.run(self.router.manage_releases(
            operation="get_release",
            params={"release_id": "release-123"}
        ))

        self.assertIn("results", result)
        self.assertEqual(result["operation"], "get_release")

    def test_get_release_missing_id(self):
        """Test get_release without release_id"""
        result = asyncio.run(self.router.manage_releases(
            operation="get_release"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("release_id", (result.get("error") or result.get("message", "")).lower())

    def test_create_release(self):
        """Test create_release operation"""
        async def mock_create(*args, **kwargs):
            return {"id": "new-release", "name": "frontend/release-2000"}

        self.mock_releases.create_release = mock_create

        result = asyncio.run(self.router.manage_releases(
            operation="create_release",
            params={
                "name": "frontend/release-2000",
                "start": 1742349976000,
                "applications": [{"name": "My App"}]
            }
        ))

        self.assertIn("results", result)

    def test_create_release_missing_name(self):
        """Test create_release without name"""
        result = asyncio.run(self.router.manage_releases(
            operation="create_release",
            params={"start": 1742349976000}
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("name", (result.get("error") or result.get("message", "")).lower())

    def test_create_release_missing_start(self):
        """Test create_release without start"""
        result = asyncio.run(self.router.manage_releases(
            operation="create_release",
            params={"name": "frontend/release-2000"}
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("start", (result.get("error") or result.get("message", "")).lower())

    def test_update_release(self):
        """Test update_release operation"""
        async def mock_update(*args, **kwargs):
            return {"id": "release-123", "name": "frontend/release-2001"}

        self.mock_releases.update_release = mock_update

        result = asyncio.run(self.router.manage_releases(
            operation="update_release",
            params={
                "release_id": "release-123",
                "name": "frontend/release-2001",
                "start": 1742349976000
            }
        ))

        self.assertIn("results", result)

    def test_update_release_missing_id(self):
        """Test update_release without release_id"""
        result = asyncio.run(self.router.manage_releases(
            operation="update_release",
            params={"name": "frontend/release-2001", "start": 1742349976000}
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("release_id", (result.get("error") or result.get("message", "")).lower())

    def test_delete_release(self):
        """Test delete_release operation"""
        async def mock_delete(*args, **kwargs):
            return {"success": True}

        self.mock_releases.delete_release = mock_delete

        result = asyncio.run(self.router.manage_releases(
            operation="delete_release",
            params={"release_id": "release-123"}
        ))

        self.assertIn("results", result)

    def test_delete_release_missing_id(self):
        """Test delete_release without release_id"""
        result = asyncio.run(self.router.manage_releases(
            operation="delete_release"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("release_id", (result.get("error") or result.get("message", "")).lower())

    def test_exception_handling(self):
        """Test exception handling in router"""
        async def mock_error(*args, **kwargs):
            raise Exception("Test error")

        self.mock_releases.get_all_releases = mock_error

        result = asyncio.run(self.router.manage_releases(
            operation="get_all_releases"
        ))

        self.assertTrue("error" in result or result.get("elicitation_needed"))
        self.assertIn("Test error", str((result.get("error") or result.get("message", ""))))

    def test_params_none_handling(self):
        """Test handling when params is None"""
        async def mock_get_all(*args, **kwargs):
            return {"releases": []}

        self.mock_releases.get_all_releases = mock_get_all

        result = asyncio.run(self.router.manage_releases(
            operation="get_all_releases",
            params=None
        ))

        self.assertIn("results", result)


if __name__ == '__main__':
    unittest.main()

