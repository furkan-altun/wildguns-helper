"""
CredentialStore: Çerez string'ini yerel dosyaya kaydeder.

Windows Credential Manager uzun string'leri reddediyor, bu yüzden
uygulama dizinindeki gizli bir dosyaya yazıyoruz.
"""
from __future__ import annotations

import os
import base64


def _config_path() -> str:
    """Çerez dosyasının yolunu döner (uygulama dizini veya %APPDATA%)."""
    app_data = os.environ.get("APPDATA") or os.path.expanduser("~")
    folder = os.path.join(app_data, "WildgunsTracker")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, ".session")


class CredentialStore:
    """Çerez string'ini yerel dosyaya kaydeden/okuyan sınıf."""

    SERVICE_NAME = "wildguns-tracker"  # geriye dönük uyumluluk için

    def save(self, cookie_str: str, _password: str = "") -> None:
        """Çerez string'ini dosyaya kaydeder."""
        encoded = base64.b64encode(cookie_str.encode()).decode()
        with open(_config_path(), "w", encoding="utf-8") as f:
            f.write(encoded)

    def load(self) -> tuple[str, str] | None:
        """Kaydedilmiş çerez string'ini döner; yoksa None döner."""
        path = _config_path()
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                encoded = f.read().strip()
            cookie_str = base64.b64decode(encoded).decode()
            return (cookie_str, "")
        except Exception:
            return None

    def delete(self) -> None:
        """Kaydedilmiş çerez dosyasını siler."""
        path = _config_path()
        if os.path.exists(path):
            os.remove(path)
