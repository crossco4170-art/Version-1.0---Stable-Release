from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


NavigationFactory = Callable[[ctk.CTkFrame], ctk.CTkFrame]


class NavigationController:
    """Manages view lifecycle and deterministic navigation routing."""

    def __init__(self, content_host: ctk.CTkFrame) -> None:
        self.content_host = content_host
        self._factories: dict[str, NavigationFactory] = {}
        self._instances: dict[str, ctk.CTkFrame] = {}
        self.current_view_key: str | None = None

    def register(self, key: str, factory: NavigationFactory) -> None:
        self._factories[key] = factory

    def keys(self) -> list[str]:
        return list(self._factories.keys())

    def show(self, key: str) -> ctk.CTkFrame:
        if key not in self._factories:
            raise KeyError(f"Unknown navigation key: {key}")

        if self.current_view_key == key and key in self._instances:
            return self._instances[key]

        for view in self._instances.values():
            view.grid_remove()

        if key not in self._instances:
            self._instances[key] = self._factories[key](self.content_host)

        selected = self._instances[key]
        selected.grid(row=0, column=0, sticky="nsew")
        self.current_view_key = key
        return selected
