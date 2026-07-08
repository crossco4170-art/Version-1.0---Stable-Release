from __future__ import annotations

from collections.abc import Callable


ControllerObserver = Callable[[str, object], None]


class BaseController:
    """Shared controller contract for AppState binding and event propagation."""

    def __init__(self) -> None:
        self._app_state: object | None = None
        self._observers: list[ControllerObserver] = []

    def bind_app_state(self, app_state: object) -> None:
        """Bind to an AppState-like object and subscribe to state events."""
        if self._app_state is app_state:
            return

        if self._app_state is not None:
            self.unbind_app_state()

        self._app_state = app_state
        if hasattr(app_state, "add_observer"):
            app_state.add_observer(self.on_state_changed)

    def unbind_app_state(self) -> None:
        """Unbind from current AppState and remove state event subscription."""
        if self._app_state is not None and hasattr(self._app_state, "remove_observer"):
            self._app_state.remove_observer(self.on_state_changed)
        self._app_state = None

    def register_observer(self, observer: ControllerObserver) -> None:
        """Register an observer that receives controller-level state events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: ControllerObserver) -> None:
        """Unregister a previously added controller observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def on_state_changed(self, field_name: str, value: object) -> None:
        """Default state-change handler; subclasses can override and call super()."""
        for observer in list(self._observers):
            observer(field_name, value)