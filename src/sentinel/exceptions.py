from typing import Optional, Any

class CloudTrailParsingError(Exception):
    def __init__(self, message, errors = None):
        super().__init__(message)
        self.errors : Optional[Any] = errors

class NormalizationError(Exception):
    def __init__(self, message, errors = None):
        super().__init__(message)
        self.errors : Optional[Any] = errors