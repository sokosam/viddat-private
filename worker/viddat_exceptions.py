class AWS_error(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class vidGen_error(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class video_upload_error(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

