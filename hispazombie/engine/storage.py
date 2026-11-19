"""Almacenamiento de partidas guardadas.

* Escritorio: archivos JSON en la carpeta de datos del usuario.
* Navegador (pygbag): localStorage del navegador.

Las dos implementaciones tienen la misma interfaz (read / write / exists / delete), así
que el resto del juego no necesita saber dónde se guarda.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

APP_NAME = "HispaZombie"


def default_save_dir() -> str:
    """Carpeta de partidas según el sistema operativo."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(base, APP_NAME)


class FileStorage:
    def __init__(self, folder: str) -> None:
        self.folder = folder

    def _path(self, key: str) -> str:
        return os.path.join(self.folder, f"{key}.json")

    def exists(self, key: str) -> bool:
        return os.path.exists(self._path(key))

    def read(self, key: str) -> dict[str, Any] | None:
        if not self.exists(key):
            return None
        with open(self._path(key), encoding="utf-8") as f:
            return json.load(f)

    def write(self, key: str, data: dict[str, Any]) -> None:
        os.makedirs(self.folder, exist_ok=True)
        tmp = self._path(key) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self._path(key))  # escritura atómica: no deja archivos a medias

    def delete(self, key: str) -> None:
        if self.exists(key):
            os.remove(self._path(key))


class BrowserStorage:
    """localStorage del navegador, accesible desde pygbag con el módulo `platform`."""

    PREFIX = f"{APP_NAME}:"

    def __init__(self) -> None:
        import platform  # en pygbag, este módulo da acceso a window

        self._storage = platform.window.localStorage

    def exists(self, key: str) -> bool:
        return self._storage.getItem(self.PREFIX + key) is not None

    def read(self, key: str) -> dict[str, Any] | None:
        raw = self._storage.getItem(self.PREFIX + key)
        return json.loads(raw) if raw else None

    def write(self, key: str, data: dict[str, Any]) -> None:
        self._storage.setItem(self.PREFIX + key, json.dumps(data, ensure_ascii=False))

    def delete(self, key: str) -> None:
        self._storage.removeItem(self.PREFIX + key)


class MemoryStorage:
    """Almacenamiento en memoria: para tests, o si no hay ningún otro disponible."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def exists(self, key: str) -> bool:
        return key in self._data

    def read(self, key: str) -> dict[str, Any] | None:
        raw = self._data.get(key)
        return json.loads(raw) if raw else None

    def write(self, key: str, data: dict[str, Any]) -> None:
        self._data[key] = json.dumps(data)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


def create_storage():
    if sys.platform == "emscripten":
        try:
            return BrowserStorage()
        except Exception:  # noqa: BLE001 - sin localStorage: partida solo en memoria
            return MemoryStorage()
    return FileStorage(default_save_dir())
