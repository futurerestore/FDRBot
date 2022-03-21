class FDRError(Exception):
    pass


class StopCommand(FDRError):
    pass


class ViewTimeoutException(FDRError):
    def __init__(self, timeout: int, *args) -> None:
        super().__init__(*args)
        self.timeout = timeout
