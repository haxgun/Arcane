from typing import Any


class AuthenticationError(Exception):
    pass


class HTTPException(Exception):
    def __init__(
        self, message: str, *, reason: str | None = None, status: int | None = None, extra: Any | None = None
    ):
        self.message = f'{status}: {message}: {reason}'
        self.reason = reason
        self.status = status
        self.extra = extra

        super().__init__(self.message)
