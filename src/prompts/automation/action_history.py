from typing import Optional

from src.prompts import auto_register_prompt


class ActionHistoryPrompts:
    """Class containing automation action history related prompts"""

    @auto_register_prompt
    @staticmethod
    def submit_automation_action(payload: dict) -> str:
        """Submit an automation action for execution on an agent"""
        return f"""
        Submit automation action:
        - Payload: {payload}

        Required fields in payload:
        - actionId: Action identifier of the action to run
        - hostId: Agent host identifier on which to run the action

        Optional fields:
        - async: "true" if the action should be run in asynchronous mode (default: "true")
        - eventId: Event identifier (incident or issue) associated with the policy
        - policyId: Policy identifier that associates the action trigger to the action
        - timeout: Action run timeout in seconds (default: 30)
        - inputParameters: Array of action run input parameters
        """

    @auto_register_prompt
    @staticmethod
    def get_action_instance_details(
        action_instance_id: str,
        window_size: Optional[int] = None,
        to: Optional[int] = None,
    ) -> str:
        """Get the details of an automation action run result by ID from action run history"""
        return f"""
        Get action instance details:
        - Action instance ID: {action_instance_id}
        - Window size: {window_size or 'default (10 minutes)'}
        - To timestamp: {to or 'current time'}
        """

    @auto_register_prompt
    @staticmethod
    def list_action_instances(
        window_size: Optional[int] = None,
        to: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        target_snapshot_id: Optional[str] = None,
        event_id: Optional[str] = None,
        event_specification_id: Optional[str] = None,
        search: Optional[str] = None,
        types: Optional[list] = None,
        action_statuses: Optional[list] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> str:
        """Get the details of automation action run results from action run history"""
        return f"""
        List action instances:
        - Window size: {window_size or 'None'}
        - To timestamp: {to or 'None'}
        - Page: {page or 'None'}
        - Page size: {page_size or 'None'}
        - Target snapshot ID: {target_snapshot_id or 'None'}
        - Event ID: {event_id or 'None'}
        - Event specification ID: {event_specification_id or 'None'}
        - Search: {search or 'None'}
        - Types: {types or 'None'}
        - Action statuses: {action_statuses or 'None'}
        - Order by: {order_by or 'None'}
        - Order direction: {order_direction or 'None'}

        Steps:
        1. Apply filters to narrow down action execution history
        2. Paginate through results using page and page_size
        3. Filter by status (SUCCESS, FAILED), snapshot, event, or search term
        4. Sort results using order_by and order_direction

        Related coverage:
        - For maintenance window operations (create, modify, close, list, validate, templates),
          use the manage_maintenance_windows tool with resource_type="window" or "templates"
        - For event queries (incidents, issues, changes, Kubernetes info events, agent monitoring events),
          use the manage_events tool with the appropriate operation
        """

    @auto_register_prompt
    @staticmethod
    def delete_action_instance(
        action_instance_id: str,
        from_time: int,
        to_time: int,
    ) -> str:
        """Delete an automation action run result from the action run history by ID"""
        return f"""
        Delete action instance:
        - Action instance ID: {action_instance_id}
        - From time: {from_time}
        - To time: {to_time}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('submit_automation_action', cls.submit_automation_action),
            ('get_action_instance_details', cls.get_action_instance_details),
            ('list_action_instances', cls.list_action_instances),
            ('delete_action_instance', cls.delete_action_instance),
        ]
