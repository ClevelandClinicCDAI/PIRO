class ExternalAPIError(Exception):
    """An expected failure safe to expose through the external API."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        retry_after: int | None = None,
    ) -> None:
        """Describe a public failure without exposing internal exception
        details."""
        self.status: int = status
        self.code: str = code
        self.message: str = message
        self.retry_after: int | None = retry_after
        super().__init__(code)
