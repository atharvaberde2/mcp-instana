from typing import Optional

from src.prompts import auto_register_prompt


class ActionCatalogPrompts:
    """Class containing automation action catalog related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_action_matches(
        payload: dict,
        target_snapshot_id: Optional[str] = None,
    ) -> str:
        """Get action matches for a given action search space and target snapshot ID"""
        return f"""
        Get action matches:
        - Payload: {payload}
        - Target snapshot ID: {target_snapshot_id or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def get_actions() -> str:
        """Get a list of available automation actions from the action catalog"""
        return """
        Get all available automation actions from the action catalog.
        Returns cleaned action data optimized for LLM consumption.

        Steps:
        1. Fetch all automation actions from the catalog
        2. Return cleaned action data with names, descriptions, and types

        Related coverage:
        - For maintenance window operations (create, modify, close, list, validate, templates),
          use the manage_maintenance_windows tool with resource_type="window" or "templates"
        - For event queries (incidents, issues, changes, Kubernetes info events, agent monitoring events),
          use the manage_events tool with the appropriate operation
        """

    @auto_register_prompt
    @staticmethod
    def get_action_details(action_id: str) -> str:
        """Get detailed information about a specific automation action by ID"""
        return f"""
        Get action details:
        - Action ID: {action_id}
        """

    @auto_register_prompt
    @staticmethod
    def get_action_types() -> str:
        """Get a list of available action types in the action catalog"""
        return """
        Get all available action types from the action catalog.
        """

    @auto_register_prompt
    @staticmethod
    def get_action_tags() -> str:
        """Get a list of available action tags from the action catalog"""
        return """
        Get all available action tags from the action catalog.
        """

    @auto_register_prompt
    @staticmethod
    def get_action_matches_by_id_and_time_window(
        application_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        to: Optional[int] = None,
        window_size: Optional[int] = None,
    ) -> str:
        """Get automation actions that match based on application ID or snapshot ID within a specified time window"""
        return f"""
        Get action matches by ID and time window:
        - Application ID: {application_id or 'None'}
        - Snapshot ID: {snapshot_id or 'None'}
        - To timestamp: {to or 'None'}
        - Window size: {window_size or 'None'}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_action_matches', cls.get_action_matches),
            ('get_actions', cls.get_actions),
            ('get_action_details', cls.get_action_details),
            ('get_action_types', cls.get_action_types),
            ('get_action_tags', cls.get_action_tags),
            ('get_action_matches_by_id_and_time_window', cls.get_action_matches_by_id_and_time_window),
        ]
