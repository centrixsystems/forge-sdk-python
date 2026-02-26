"""Error types for the Forge SDK."""


class ForgeError(Exception):
    """Base exception for Forge SDK errors."""


class ForgeServerError(ForgeError):
    """The server returned a 4xx/5xx response."""

    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(f"server error ({status}): {message}")


class ForgeConnectionError(ForgeError):
    """Failed to connect to the Forge server."""

    def __init__(self, cause: Exception) -> None:
        self.cause = cause
        super().__init__(f"connection error: {cause}")
