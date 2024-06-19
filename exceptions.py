class TaskException(Exception):
    play = False
    report = True
    reload = False

    def __init__(self, *, play: bool | None = None, report: bool | None = None, reload: bool | None = None):
        if play is not None:
            self.play = play
        if report is not None:
            self.report = report
        if reload is not None:
            self.reload = reload


class SceneErrorException(TaskException):
    play = True


class SceneCriticalErrorException(TaskException):
    play = False


class ActionErrorException(TaskException):
    play = True


class ActionCriticalErrorException(TaskException):
    play = False


class InvalidConfErrorException(TaskException):
    report = False


class UnknownErrorException(TaskException):
    play = False


class StopException(TaskException):
    play = False
    report = False


class ReloadException(TaskException):
    report = False
    reload = True


class ProxyChangeException(Exception):
    pass
