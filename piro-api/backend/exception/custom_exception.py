class CustomException(Exception):
    """Custom exception class for handling specific error scenarios.

    Attributes:
        field -- name of the attribute that fails validation
        message -- explanation of the error
    """

    def __init__(self, message):
        self.field = ""
        self.message = message
        super().__init__(self.message)
