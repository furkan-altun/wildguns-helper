from PyQt6.QtCore import QSettings

RESOURCES = ["wood", "clay", "iron", "food"]


class SettingsStore:
    """Eşik değerlerini ve uygulama tercihlerini QSettings ile kalıcı olarak saklar."""

    def __init__(self) -> None:
        self._settings = QSettings("WildgunsTracker", "WildgunsTracker")

    def get_threshold(self, resource: str) -> int | None:
        """Belirtilen kaynak için eşik değerini döndürür; devre dışıysa None döner."""
        key = f"thresholds/{resource}"
        value = self._settings.value(key, defaultValue=None)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def set_threshold(self, resource: str, value: int | None) -> None:
        """Belirtilen kaynak için eşik değerini kaydeder; None devre dışı anlamına gelir."""
        key = f"thresholds/{resource}"
        if value is None:
            self._settings.setValue(key, None)
        else:
            self._settings.setValue(key, int(value))
        self._settings.sync()

    def get_all_thresholds(self) -> dict[str, int | None]:
        """Tüm kaynaklar için eşik değerlerini döndürür."""
        return {resource: self.get_threshold(resource) for resource in RESOURCES}

    def set_value(self, key: str, value) -> None:
        self._settings.setValue(f"app/{key}", value)
        self._settings.sync()

    def get_value(self, key: str, default=None):
        return self._settings.value(f"app/{key}", defaultValue=default)
