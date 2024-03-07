class UpdaterActiveError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class AccessDeniedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)