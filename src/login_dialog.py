"""
SetupDialog: Chrome remote debugging bağlantısını kuran diyalog.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from src.scraper import Scraper, REMOTE_DEBUG_PORT

INSTRUCTIONS = f"""<b>Kurulum</b><br><br>
Aşağıdaki butona tıklayın. Chrome kapanıp remote debugging modunda yeniden açılacak.<br><br>
Oyuna giriş yapın, ardından <b>Bağlan</b> butonuna basın.<br><br>
<i>Not: Mevcut Chrome profiliniz kullanılır, giriş bilgileriniz korunur.</i>"""


class CookieDialog(QDialog):
    """Chrome remote debugging bağlantısını kuran diyalog."""

    def __init__(self, scraper: Scraper, credential_store=None, parent=None) -> None:
        super().__init__(parent)
        self._scraper = scraper
        self.setWindowTitle("Wildguns — Chrome Bağlantısı")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.setStyleSheet("""
            QDialog, QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', Arial; font-size: 13px; }
            QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 5px; padding: 6px 14px; }
            QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }
            QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }
            QLabel { color: #cdd6f4; }
        """)

        title = QLabel("<b>Wildguns Kaynak Takip — Kurulum</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel(INSTRUCTIONS)
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        btn_launch = QPushButton("🚀 Chrome'u Başlat (remote debugging)")
        btn_launch.clicked.connect(self._on_launch_chrome)
        layout.addWidget(btn_launch)

        self._btn_connect = QPushButton("✅ Bağlan")
        self._btn_connect.setDefault(True)
        self._btn_connect.clicked.connect(self._on_connect)
        layout.addWidget(self._btn_connect)

    def _on_launch_chrome(self) -> None:
        """Chrome'u remote debugging modunda başlatır."""
        self._scraper.launch_chrome()
        if self._scraper.is_logged_in():
            self._show_msg("Chrome açıldı. Oyuna giriş yapın, ardından 'Bağlan'a basın.", error=False)
        else:
            self._show_msg(
                "Chrome bulunamadı veya açılamadı.\n"
                f"Manuel olarak başlatın: chrome.exe --remote-debugging-port={REMOTE_DEBUG_PORT}",
                error=True,
            )

    def _show_msg(self, msg: str, error: bool = True) -> None:
        self._error_label.setText(msg)
        self._error_label.setStyleSheet("color: red;" if error else "color: green;")
        self._error_label.setVisible(True)

    def _on_connect(self) -> None:
        self._error_label.setVisible(False)
        self._btn_connect.setEnabled(False)
        self._btn_connect.setText("Bağlanıyor…")

        try:
            if not self._scraper.is_logged_in():
                self._show_msg(
                    f"Chrome remote debugging portu ({REMOTE_DEBUG_PORT}) bulunamadı.\n"
                    "Lütfen önce 'Chrome'u Başlat' butonuna basın ve oyuna giriş yapın."
                )
                return
            self.accept()
        finally:
            self._btn_connect.setEnabled(True)
            self._btn_connect.setText("✅ Bağlan")
