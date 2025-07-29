"""
Custom exceptions for RedEval.
"""


class RedEvalError(Exception):
    """Base exception for RedEval."""
    pass


class ConfigurationError(RedEvalError):
    """Raised when there's a configuration error."""
    pass


class ModelError(RedEvalError):
    """Raised when there's a model-related error."""
    pass


class EvaluationError(RedEvalError):
    """Raised when evaluation fails."""
    pass


class PipelineError(RedEvalError):
    """Raised when pipeline execution fails."""
    pass


class AuthenticationError(RedEvalError):
    """Raised when authentication fails."""
    pass
