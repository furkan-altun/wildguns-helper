"""
Uygulama giriş noktası.
"""
from __future__ import annotations

import logging
import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from src.alarm_manager import AlarmManager
from src.login_dialog import CookieDialog
from src.main_window import MainWindow
from src.resource_tracker import ResourceTracker
from src.scraper import Scraper
from src.settings_store import SettingsStore


def _setup_crash_log() -> None:
    log_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "WildgunsTracker", "app.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        encoding="utf-8",
    )

    def handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logging.critical("Yakalanmayan hata:\n" + "".join(traceback.format_exception(exc_type, exc_value, exc_tb)))

    sys.excepthook = handle_exception


def run() -> None:
    _setup_crash_log()
    app = QApplication(sys.argv)
    app.setApplicationName("WildgunsTracker")
    app.setOrganizationName("WildgunsTracker")

    settings_store = SettingsStore()
    scraper = Scraper()

    # Chrome bağlantısı yoksa otomatik başlat
    if not scraper.is_logged_in():
        scraper.launch_chrome()
        dialog = CookieDialog(scraper=scraper)
        if dialog.exec() != CookieDialog.DialogCode.Accepted:
            sys.exit(0)

    alarm_manager = AlarmManager()
    tracker = ResourceTracker(scraper=scraper)
    window = MainWindow(
        tracker=tracker,
        alarm_manager=alarm_manager,
        settings_store=settings_store,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run()
