from __future__ import annotations

from controllers.base_controller import BaseController


class _FakeAppState:
    def __init__(self) -> None:
        self._observers: list[object] = []

    def add_observer(self, observer: object) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: object) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def emit(self, field_name: str, value: object) -> None:
        for observer in list(self._observers):
            observer(field_name, value)


def test_bind_app_state_registers_state_handler() -> None:
    controller = BaseController()
    app_state = _FakeAppState()

    controller.bind_app_state(app_state)

    assert controller.on_state_changed in app_state._observers


def test_unbind_app_state_unregisters_state_handler() -> None:
    controller = BaseController()
    app_state = _FakeAppState()
    controller.bind_app_state(app_state)

    controller.unbind_app_state()

    assert controller.on_state_changed not in app_state._observers


def test_bind_new_app_state_unbinds_previous_one() -> None:
    controller = BaseController()
    first = _FakeAppState()
    second = _FakeAppState()

    controller.bind_app_state(first)
    controller.bind_app_state(second)

    assert controller.on_state_changed not in first._observers
    assert controller.on_state_changed in second._observers


def test_register_and_unregister_observer() -> None:
    controller = BaseController()
    calls: list[tuple[str, object]] = []

    def observer(field_name: str, value: object) -> None:
        calls.append((field_name, value))

    controller.register_observer(observer)
    controller.on_state_changed("selected_applicant", 101)
    controller.unregister_observer(observer)
    controller.on_state_changed("selected_applicant", 202)

    assert calls == [("selected_applicant", 101)]


def test_register_observer_deduplicates_listener() -> None:
    controller = BaseController()
    calls: list[tuple[str, object]] = []

    def observer(field_name: str, value: object) -> None:
        calls.append((field_name, value))

    controller.register_observer(observer)
    controller.register_observer(observer)
    controller.on_state_changed("selected_applicant", 333)

    assert calls == [("selected_applicant", 333)]