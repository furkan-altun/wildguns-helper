"""
AlarmManager: Kaynak eşik kontrolü ve sesli alarm yönetimi.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl

from src.models import ResourceTotals

RESOURCES = ["wood", "clay", "iron", "food"]


class AlarmManager(QObject):
    """Kaynak eşiklerini kontrol eder ve alarm sinyalleri yayınlar."""

    alarm_triggered = pyqtSignal(str, int)  # kaynak_adı, miktar
    alarm_silenced = pyqtSignal(str)        # kaynak_adı

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        # Susturulmuş kaynaklar kümesi
        self._silenced: set[str] = set()
        # Bir önceki kontrol döngüsünde eşiğin altında olan kaynaklar
        # (susturma sıfırlama için izlenir)
        self._below_threshold: set[str] = set()
        # Ses efekti
        self._sound = QSoundEffect(self)
        self._sound_loaded = False
        self._try_load_sound()

    # ------------------------------------------------------------------
    # Ses yükleme
    # ------------------------------------------------------------------

    def _try_load_sound(self) -> None:
        """Alarm ses dosyasını yüklemeye çalışır; yoksa sessizce devam eder."""
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "assets", "alarm.wav"),
            os.path.join(os.path.dirname(__file__), "alarm.wav"),
        ]
        for path in candidates:
            abs_path = os.path.abspath(path)
            if os.path.isfile(abs_path):
                self._sound.setSource(QUrl.fromLocalFile(abs_path))
                self._sound_loaded = True
                break

    def _play_sound(self) -> None:
        """Ses dosyası yüklüyse çalar; değilse sessizce devam eder."""
        if self._sound_loaded:
            try:
                self._sound.play()
            except Exception:
                pass  # Ses çalma hatası sessizce loglanır

    # ------------------------------------------------------------------
    # Eşik kontrolü
    # ------------------------------------------------------------------

    def check_thresholds(
        self,
        totals: ResourceTotals,
        thresholds: dict[str, int | None],
    ) -> None:
        """
        Her kaynak için eşik kontrolü yapar.

        - Eşik None ise alarm tetiklenmez.
        - Toplam >= eşik ise alarm_triggered sinyali yayınlanır
          (susturulmamışsa).
        - Toplam < eşik ise kaynak "eşik altı" olarak işaretlenir;
          susturma durumu otomatik sıfırlanır.
        """
        for resource in RESOURCES:
            threshold = thresholds.get(resource)
            amount: int = getattr(totals, resource, 0)

            if threshold is None:
                # Devre dışı eşik — alarm tetiklenmez
                continue

            if amount < threshold:
                # Eşiğin altına düştü → susturmayı sıfırla
                self._below_threshold.add(resource)
                if resource in self._silenced:
                    self._silenced.discard(resource)
            else:
                # Eşiğe ulaştı veya aştı
                if resource in self._below_threshold:
                    # Eşiğin altından tekrar eşiğe geldi → susturmayı sıfırla
                    self._silenced.discard(resource)
                    self._below_threshold.discard(resource)

                if resource not in self._silenced:
                    self.alarm_triggered.emit(resource, amount)
                    self._play_sound()

    # ------------------------------------------------------------------
    # Susturma yönetimi
    # ------------------------------------------------------------------

    def silence(self, resource: str) -> None:
        """Belirtilen kaynak için alarmı susturur."""
        self._silenced.add(resource)
        self.alarm_silenced.emit(resource)

    def reset_silence(self, resource: str) -> None:
        """Belirtilen kaynak için susturma durumunu manuel olarak sıfırlar."""
        self._silenced.discard(resource)
        self._below_threshold.discard(resource)
