class AgentForgeError(Exception):
    """Base exception for app errors."""


class PlanValidationError(AgentForgeError):
    pass


class PolicyViolationError(AgentForgeError):
    pass


class ToolExecutionError(AgentForgeError):
    pass


class RetrievalError(AgentForgeError):
    pass


class ApprovalError(AgentForgeError):
    pass
