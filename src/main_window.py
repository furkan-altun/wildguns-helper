"""
MainWindow: Ana pencere bileşeni.
"""
from __future__ import annotations

import logging
import traceback
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models import ResourceTotals, VillageData
from src.settings_store import SettingsStore
from src.credential_store import CredentialStore

if TYPE_CHECKING:
    from src.alarm_manager import AlarmManager
    from src.resource_tracker import ResourceTracker

RESOURCE_COLUMNS: list[tuple[str, str]] = [
    ("wood", "Odun"),
    ("clay", "Kil"),
    ("iron", "Demir"),
    ("food", "Yiyecek"),
]

COL_NAME = 0
COL_WOOD = 1
COL_CLAY = 2
COL_IRON = 3
COL_FOOD = 4
COL_TOTAL = 5

DEFAULT_INTERVAL_SECS = 60

APP_STYLE = """
    QMainWindow, QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }
    QPushButton {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 5px;
        padding: 5px 12px;
        font-size: 12px;
    }
    QPushButton:hover { background-color: #45475a; border-color: #89b4fa; }
    QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }
    QPushButton:disabled { background-color: #181825; color: #585b70; border-color: #313244; }
    QTabWidget::pane { border: 1px solid #45475a; border-radius: 4px; }
    QTabBar::tab {
        background-color: #313244;
        color: #a6adc8;
        border: 1px solid #45475a;
        border-bottom: none;
        padding: 5px 16px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected { background-color: #1e1e2e; color: #cdd6f4; }
    QTabBar::tab:hover { background-color: #45475a; }
    QTableWidget {
        background-color: #181825;
        color: #cdd6f4;
        gridline-color: #313244;
        border: 1px solid #45475a;
        border-radius: 4px;
        selection-background-color: #313244;
    }
    QTableWidget::item { padding: 4px 8px; color: #cdd6f4; }
    QTableWidget::item:selected { background-color: #45475a; color: #cdd6f4; }
    QHeaderView::section {
        background-color: #313244;
        color: #89b4fa;
        border: none;
        border-right: 1px solid #45475a;
        border-bottom: 1px solid #45475a;
        padding: 5px 8px;
        font-weight: bold;
    }
    QPlainTextEdit {
        background-color: #181825;
        color: #cdd6f4;
        border: none;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
    }
    QGroupBox {
        background-color: #181825;
        border: 1px solid #45475a;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
        color: #89b4fa;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: #89b4fa;
    }
    QSpinBox {
        background-color: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 3px 6px;
    }
    QSpinBox:focus { border-color: #89b4fa; }
    QSpinBox::up-button, QSpinBox::down-button { background-color: #45475a; border: none; width: 16px; }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #585b70; }
    QRadioButton { color: #cdd6f4; spacing: 6px; }
    QRadioButton::indicator {
        width: 14px; height: 14px;
        border: 1px solid #45475a;
        border-radius: 7px;
        background-color: #313244;
    }
    QRadioButton::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }
    QLabel { color: #cdd6f4; }
    QStatusBar {
        background-color: #181825;
        color: #a6adc8;
        border-top: 1px solid #313244;
    }
"""


class _QtLogHandler(logging.Handler):
    """Python logging mesajlarını QPlainTextEdit'e yönlendiren handler."""

    def __init__(self, widget: QPlainTextEdit) -> None:
        super().__init__()
        self._widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._widget.appendPlainText(msg)
        except Exception:
            pass


class MainWindow(QMainWindow):

    def __init__(
        self,
        tracker: "ResourceTracker",
        alarm_manager: "AlarmManager",
        settings_store: "SettingsStore",
        credential_store: "CredentialStore | None" = None,
    ) -> None:
        super().__init__()
        self._tracker = tracker
        self._alarm_manager = alarm_manager
        self._settings_store = settings_store
        self._credential_store = credential_store

        self._last_updated: datetime | None = None
        self._next_refresh: datetime | None = None
        self._last_totals: ResourceTotals | None = None
        self._goal_was_reached: bool = False

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(1000)
        self._status_timer.timeout.connect(self._update_status_bar)
        self._status_timer.start()

        self._setup_ui()
        self._setup_logging()
        self._connect_signals()

        # Kaydedilmiş aralık değerini yükle
        saved_interval = self._settings_store.get_value("interval_secs", DEFAULT_INTERVAL_SECS)
        try:
            self._spin_interval.setValue(int(saved_interval))
        except (ValueError, TypeError):
            pass

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        self.setWindowTitle("Wildguns Kaynak Takip")
        self.setMinimumSize(820, 560)
        self.setStyleSheet(APP_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addLayout(self._build_control_bar())

        # Tab widget
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, stretch=1)

        # Sekme 1: Kaynaklar
        resources_widget = QWidget()
        res_layout = QVBoxLayout(resources_widget)
        res_layout.setContentsMargins(4, 4, 4, 4)
        res_layout.setSpacing(6)
        self._table = self._build_table()
        res_layout.addWidget(self._table, stretch=1)
        res_layout.addWidget(self._build_goal_group(), stretch=0)
        self._tabs.addTab(resources_widget, "📊 Kaynaklar")

        # Sekme 2: Log
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(4, 4, 4, 4)
        log_layout.setSpacing(4)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMaximumBlockCount(500)  # max 500 satır
        log_layout.addWidget(self._log_view)

        btn_clear = QPushButton("🗑 Logları Temizle")
        btn_clear.setFixedWidth(160)
        btn_clear.clicked.connect(self._log_view.clear)
        log_layout.addWidget(btn_clear, alignment=Qt.AlignmentFlag.AlignRight)

        self._tabs.addTab(log_widget, "📋 Log")

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._lbl_last_update = QLabel("Son güncelleme: —")
        self._lbl_next_refresh = QLabel("Sonraki yenileme: —")
        self._status_bar.addWidget(self._lbl_last_update)
        self._status_bar.addPermanentWidget(self._lbl_next_refresh)

        self._btn_silence: QPushButton | None = None
        self._alarm_resource: str | None = None

    def _setup_logging(self) -> None:
        """Python root logger'ı log sekmesine ve dosyaya yönlendirir."""
        import os
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

        # Sadece ERROR ve üstünü UI'ya yaz
        ui_handler = _QtLogHandler(self._log_view)
        ui_handler.setFormatter(fmt)
        ui_handler.setLevel(logging.ERROR)

        # Dosyaya her şeyi yaz (crash sonrası inceleme için)
        log_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "WildgunsTracker", "app.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.DEBUG)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(ui_handler)
        root.addHandler(file_handler)

        logging.info("Uygulama başlatıldı.")

    def log(self, level: str, message: str) -> None:
        """Doğrudan log sekmesine mesaj yazar ve Log sekmesini kırmızı işaretler."""
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_view.appendPlainText(f"{ts} [{level}] {message}")
        if level in ("ERROR", "WARNING"):
            idx = self._tabs.indexOf(self._log_view.parent())
            self._tabs.setTabText(idx, "📋 Log ⚠")

    def _build_control_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self._btn_start = QPushButton("▶ Otomatik Başlat")
        self._btn_stop = QPushButton("■ Durdur")
        self._btn_analyze = QPushButton("🔍 Analiz Et")
        self._btn_stop.setEnabled(False)
        self._btn_start.clicked.connect(self._on_start)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_analyze.clicked.connect(self._on_refresh)

        lbl_interval = QLabel("Aralık (sn):")
        self._spin_interval = QSpinBox()
        self._spin_interval.setRange(1, 3600)
        self._spin_interval.setValue(DEFAULT_INTERVAL_SECS)
        self._spin_interval.setFixedWidth(70)
        self._spin_interval.setKeyboardTracking(False)
        self._spin_interval.valueChanged.connect(self._on_interval_changed)

        layout.addWidget(self._btn_start)
        layout.addWidget(self._btn_stop)
        layout.addWidget(self._btn_analyze)
        layout.addSpacing(16)
        layout.addWidget(lbl_interval)
        layout.addWidget(self._spin_interval)
        layout.addStretch()
        return layout

    def _build_table(self) -> QTableWidget:
        headers = ["Köy Adı", "Odun", "Kil", "Demir", "Yiyecek", "Genel Toplam"]
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setMinimumSectionSize(80)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(120)
        return table

    def _build_goal_group(self) -> QGroupBox:
        group = QGroupBox("🎯 Hedef (Bina / Upgrade Maliyeti)")
        outer = QVBoxLayout(group)
        outer.setSpacing(8)

        mode_row = QHBoxLayout()
        self._radio_grand = QRadioButton("Genel toplam hedefine göre alarm")
        self._radio_resources = QRadioButton("Kaynak toplamına göre alarm")
        self._radio_grand.setChecked(True)
        self._radio_grand.toggled.connect(self._on_goal_changed)
        mode_row.addWidget(self._radio_grand)
        mode_row.addSpacing(24)
        mode_row.addWidget(self._radio_resources)
        mode_row.addStretch()
        outer.addLayout(mode_row)

        grand_row = QHBoxLayout()
        grand_row.addWidget(QLabel("Genel toplam hedefi:"))
        self._goal_grand_spin = QSpinBox()
        self._goal_grand_spin.setRange(0, 99_999_999)
        self._goal_grand_spin.setValue(0)
        self._goal_grand_spin.setSingleStep(100)
        self._goal_grand_spin.setMinimumWidth(130)
        self._goal_grand_spin.valueChanged.connect(self._on_goal_changed)
        grand_row.addWidget(self._goal_grand_spin)
        grand_row.addStretch()
        outer.addLayout(grand_row)

        self._goal_spinboxes: dict[str, QSpinBox] = {}
        resource_row = QHBoxLayout()
        resource_row.setSpacing(12)
        for resource, label in RESOURCE_COLUMNS:
            col = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin = QSpinBox()
            spin.setRange(0, 9_999_999)
            spin.setValue(0)
            spin.setSingleStep(100)
            spin.setMinimumWidth(100)
            self._goal_spinboxes[resource] = spin
            spin.valueChanged.connect(self._on_goal_changed)
            col.addWidget(lbl)
            col.addWidget(spin)
            resource_row.addLayout(col)
        resource_row.addStretch()
        outer.addLayout(resource_row)

        self._goal_progress_lbl = QLabel("Hedef: —")
        self._goal_progress_lbl.setStyleSheet("color: #a6adc8; font-size: 12px;")
        outer.addWidget(self._goal_progress_lbl)

        self._goal_total_lbl = QLabel("Hedef toplamı: —  |  Mevcut genel toplam: —")
        self._goal_total_lbl.setStyleSheet("color: #89b4fa; font-size: 12px; font-weight: bold;")
        outer.addWidget(self._goal_total_lbl)

        return group

    # ------------------------------------------------------------------
    # Sinyaller
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._tracker.data_updated.connect(self._on_data_updated)
        self._tracker.error_occurred.connect(self._on_error_occurred)
        self._tracker.refresh_finished.connect(self._on_refresh_finished)
        self._alarm_manager.alarm_triggered.connect(self._on_alarm_triggered)

    # ------------------------------------------------------------------
    # Kontrol slot'ları
    # ------------------------------------------------------------------

    def _on_start(self) -> None:
        self._tracker.set_interval(self._spin_interval.value())
        self._tracker.start()
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._next_refresh = datetime.now() + timedelta(seconds=self._spin_interval.value())
        logging.info(f"Otomatik yenileme başlatıldı. Aralık: {self._spin_interval.value()}sn")

    def _on_stop(self) -> None:
        self._tracker.stop()
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._next_refresh = None
        self._update_status_bar()
        logging.info("Otomatik yenileme durduruldu.")

    def _on_refresh(self) -> None:
        self._tracker.refresh_now()
        logging.info("Manuel analiz başlatıldı.")

    def _on_interval_changed(self, value: int) -> None:
        self._tracker.set_interval(value)
        self._settings_store.set_value("interval_secs", value)

    # ------------------------------------------------------------------
    # Tracker slot'ları
    # ------------------------------------------------------------------

    def _on_data_updated(self, villages: list[VillageData], totals: ResourceTotals) -> None:
        try:
            self._last_totals = totals
            self._refresh_table(villages, totals)
            self._update_goal_progress(totals)
            self._check_goal_alarm(totals)
            logging.info(
                f"Veri güncellendi: {len(villages)} köy | "
                f"Toplam: Odun={totals.wood} Kil={totals.clay} Demir={totals.iron} Yiyecek={totals.food}"
            )
        except Exception:
            logging.error(f"Veri güncellenirken hata:\n{traceback.format_exc()}")

    def _on_error_occurred(self, message: str) -> None:
        logging.error(f"Scraper hatası: {message}")
        self._status_bar.showMessage(f"Hata: {message}", 10_000)
        # Log sekmesini işaretle
        log_tab_idx = self._tabs.indexOf(self._log_view.parent())
        self._tabs.setTabText(log_tab_idx, "📋 Log ⚠")
        QMessageBox.warning(self, "Hata", message)

    def _on_alarm_triggered(self, resource: str, amount: int) -> None:
        resource_labels = {"wood": "Odun", "clay": "Kil", "iron": "Demir", "food": "Yiyecek"}
        label = resource_labels.get(resource, resource)
        self._clear_silence_button()
        self._status_bar.showMessage(f"⚠ {label} eşiğe ulaştı: {amount:,}".replace(",", "."))
        self._alarm_resource = resource
        self._btn_silence = QPushButton(f"🔕 {label} Sustur")
        self._btn_silence.clicked.connect(self._on_silence_clicked)
        self._status_bar.addWidget(self._btn_silence)

    def _on_silence_clicked(self) -> None:
        if self._alarm_resource:
            self._alarm_manager.silence(self._alarm_resource)
        self._clear_silence_button()
        self._status_bar.clearMessage()

    def _clear_silence_button(self) -> None:
        if self._btn_silence is not None:
            self._status_bar.removeWidget(self._btn_silence)
            self._btn_silence.deleteLater()
            self._btn_silence = None
            self._alarm_resource = None

    def _on_refresh_finished(self, last_updated: datetime) -> None:
        self._last_updated = last_updated
        self._next_refresh = last_updated + timedelta(seconds=self._spin_interval.value())
        self._update_status_bar()

    # ------------------------------------------------------------------
    # Hedef logic
    # ------------------------------------------------------------------

    def _on_goal_changed(self) -> None:
        self._goal_was_reached = False
        self._update_goal_progress(self._last_totals)

    def _update_goal_progress(self, totals: ResourceTotals | None) -> None:
        goal = {r: self._goal_spinboxes[r].value() for r, _ in RESOURCE_COLUMNS}
        goal_sum = sum(goal.values())
        grand_target = self._goal_grand_spin.value()
        current_grand = sum(getattr(totals, r) for r, _ in RESOURCE_COLUMNS) if totals else 0
        use_grand = self._radio_grand.isChecked()

        effective_target = grand_target if use_grand else goal_sum
        if effective_target > 0:
            pct = min(100, int(current_grand / effective_target * 100))
            color = "#a6e3a1" if current_grand >= effective_target else "#f38ba8"
            self._goal_total_lbl.setText(
                f'Hedef toplamı: <b>{effective_target:,}</b>  |  '
                f'Mevcut genel toplam: <b style="color:{color}">{current_grand:,} ({pct}%)</b>'.replace(",", ".")
            )
        else:
            self._goal_total_lbl.setText(
                f'Hedef toplamı: —  |  Mevcut genel toplam: <b>{current_grand:,}</b>'.replace(",", ".")
            )

        if not use_grand and goal_sum > 0 and totals is not None:
            parts = []
            for resource, label in RESOURCE_COLUMNS:
                target = goal[resource]
                if target == 0:
                    continue
                current = getattr(totals, resource)
                pct2 = min(100, int(current / target * 100))
                c = "#a6e3a1" if current >= target else "#f38ba8"
                parts.append(f'<span style="color:{c}">{label}: {current:,}/{target:,} ({pct2}%)</span>'.replace(",", "."))
            self._goal_progress_lbl.setText("  |  ".join(parts) if parts else "Hedef: —")
        else:
            self._goal_progress_lbl.setText("Hedef: —")

    def _check_goal_alarm(self, totals: ResourceTotals) -> None:
        goal = {r: self._goal_spinboxes[r].value() for r, _ in RESOURCE_COLUMNS}
        goal_sum = sum(goal.values())
        grand_target = self._goal_grand_spin.value()
        current_grand = sum(getattr(totals, r) for r, _ in RESOURCE_COLUMNS)
        use_grand = self._radio_grand.isChecked()

        if use_grand and grand_target == 0:
            return
        if not use_grand and goal_sum == 0:
            return

        was_reached = self._goal_was_reached
        now_reached = current_grand >= (grand_target if use_grand else goal_sum)

        if now_reached and not was_reached:
            self._goal_was_reached = True
            msg = f"🎯 Hedefe ulaşıldı! Genel toplam: {current_grand:,}".replace(",", ".")
            logging.info(msg)
            self._show_alarm_popup(current_grand)
        elif not now_reached:
            self._goal_was_reached = False

    def _show_alarm_popup(self, current_grand: int) -> None:
        """Tekrar eden sesli alarm + popup gösterir. Kapatınca analiz durur."""
        # Tekrar eden ses zamanlayıcısı
        self._alarm_sound_timer = QTimer(self)
        self._alarm_sound_timer.setInterval(2000)  # her 2 saniyede bir
        self._alarm_sound_timer.timeout.connect(self._alarm_manager._play_sound)
        self._alarm_sound_timer.start()
        self._alarm_manager._play_sound()  # hemen ilk sesi çal

        # Popup dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("🎯 Hedef Tamamlandı!")
        dlg.setModal(True)
        dlg.setMinimumWidth(360)
        dlg.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dlg)
        layout.setSpacing(16)

        lbl = QLabel(
            f"<b style='font-size:15px;color:#a6e3a1;'>🎯 Hedefe ulaşıldı!</b><br><br>"
            f"Genel toplam: <b>{current_grand:,}</b><br><br>"
            f"Otomatik analiz durdurulacak.".replace(",", ".")
        )
        lbl.setTextFormat(Qt.TextFormat.RichText)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        btn = QPushButton("✅ Tamam — Analizi Durdur")
        btn.setMinimumHeight(36)
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        dlg.exec()

        # Dialog kapanınca sesi durdur ve analizi durdur
        self._alarm_sound_timer.stop()
        self._alarm_sound_timer.deleteLater()
        self._alarm_sound_timer = None
        self._on_stop()
        self._status_bar.showMessage("Hedef tamamlandı, analiz durduruldu.", 10_000)

    # ------------------------------------------------------------------
    # Tablo
    # ------------------------------------------------------------------

    def _refresh_table(self, villages: list[VillageData], totals: ResourceTotals) -> None:
        row_count = len(villages) + 1
        self._table.clearContents()
        self._table.setRowCount(row_count)
        for i, village in enumerate(villages):
            self._set_village_row(i, village)
        self._set_totals_row(row_count - 1, totals)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)

    def _set_village_row(self, row: int, village: VillageData) -> None:
        self._table.setItem(row, COL_NAME, QTableWidgetItem(village.name))
        row_total = 0
        for col_idx, (resource, _) in enumerate(RESOURCE_COLUMNS, start=1):
            amount: int = getattr(village, resource)
            row_total += amount
            item = QTableWidgetItem(f"{amount:,}".replace(",", "."))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, col_idx, item)
        total_item = QTableWidgetItem(f"{row_total:,}".replace(",", "."))
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_item.setForeground(QColor(137, 180, 250))
        self._table.setItem(row, COL_TOTAL, total_item)

    def _set_totals_row(self, row: int, totals: ResourceTotals) -> None:
        name_item = QTableWidgetItem("TOPLAM")
        f = name_item.font()
        f.setBold(True)
        name_item.setFont(f)
        self._table.setItem(row, COL_NAME, name_item)

        grand_total = 0
        for col_idx, (resource, _) in enumerate(RESOURCE_COLUMNS, start=1):
            amount: int = getattr(totals, resource)
            grand_total += amount
            item = QTableWidgetItem(f"{amount:,}".replace(",", "."))
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            fi = item.font()
            fi.setBold(True)
            item.setFont(fi)
            self._table.setItem(row, col_idx, item)

        gt_item = QTableWidgetItem(f"{grand_total:,}".replace(",", "."))
        gt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        fg = gt_item.font()
        fg.setBold(True)
        gt_item.setFont(fg)
        gt_item.setForeground(QColor(137, 180, 250))
        self._table.setItem(row, COL_TOTAL, gt_item)

    # ------------------------------------------------------------------
    # Durum çubuğu
    # ------------------------------------------------------------------

    def _update_status_bar(self) -> None:
        if self._last_updated:
            self._lbl_last_update.setText(f"Son güncelleme: {self._last_updated.strftime('%H:%M:%S')}")
        else:
            self._lbl_last_update.setText("Son güncelleme: —")

        if self._next_refresh:
            secs = max(0, int((self._next_refresh - datetime.now()).total_seconds()))
            self._lbl_next_refresh.setText(f"Sonraki yenileme: {secs}s")
        else:
            self._lbl_next_refresh.setText("Sonraki yenileme: —")
