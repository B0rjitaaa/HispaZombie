from engine.scenes import Scene, SceneManager


class LoggingScene(Scene):
    def __init__(self, name: str, log: list[str]) -> None:
        self.name = name
        self.log = log

    def on_enter(self) -> None:
        self.log.append(f"enter {self.name}")

    def on_exit(self) -> None:
        self.log.append(f"exit {self.name}")


def test_push_and_pop():
    log: list[str] = []
    manager = SceneManager()
    map_scene = LoggingScene("map", log)
    dialog = LoggingScene("dialog", log)

    manager.push(map_scene)
    manager.push(dialog)
    assert manager.current is dialog
    assert len(manager) == 2
    assert dialog.manager is manager

    assert manager.pop() is dialog
    assert manager.current is map_scene
    assert dialog.manager is None
    assert log == ["enter map", "enter dialog", "exit dialog"]


def test_replace():
    log: list[str] = []
    manager = SceneManager()
    manager.push(LoggingScene("title", log))
    manager.replace(LoggingScene("map", log))
    assert len(manager) == 1
    assert log == ["enter title", "exit title", "enter map"]


def test_pop_empty():
    manager = SceneManager()
    assert manager.pop() is None
    assert manager.empty
    assert manager.current is None
