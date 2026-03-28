"""
ResourceTracker: Periyodik scraping döngüsünü yöneten ve kaynak toplamlarını hesaplayan bileşen.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal

from src.exceptions import SessionExpiredError
from src.models import ResourceTotals, VillageData

if TYPE_CHECKING:
    from src.credential_store import CredentialStore
    from src.scraper import Scraper

DEFAULT_REFRESH_INTERVAL_MS = 60_000  # 60 saniye (varsayılan)


class _ScraperWorker(QObject):
    """
    Scraping işlemini arka planda çalıştıran worker.
    QThread içinde çalışır; UI thread'ini bloke etmez.
    """

    finished = pyqtSignal(list)   # list[VillageData]
    error = pyqtSignal(Exception)

    def __init__(self, scraper: "Scraper", parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._scraper = scraper

    def run(self) -> None:
        try:
            villages = self._scraper.fetch_villages()
            self.finished.emit(villages)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(exc)
        finally:
            # Driver'ı bu thread'de temizle
            try:
                if self._scraper._driver:
                    pass  # driver'ı açık tut, sadece thread'i bitir
            except Exception:
                pass


class ResourceTracker(QObject):
    """
    Zamanlayıcıyı yönetir, scraping döngüsünü koordine eder ve
    toplam kaynak hesaplamalarını yapar.

    Sinyaller:
        data_updated(villages, totals): Yeni veri hazır olduğunda yayınlanır.
        error_occurred(message): Kurtarılamaz hata oluştuğunda yayınlanır.
        refresh_started(): Yenileme başladığında yayınlanır.
        refresh_finished(last_updated): Yenileme tamamlandığında yayınlanır.
    """

    data_updated = pyqtSignal(list, ResourceTotals)   # villages, totals
    error_occurred = pyqtSignal(str)                   # hata mesajı
    refresh_started = pyqtSignal()
    refresh_finished = pyqtSignal(datetime)            # son güncelleme zamanı

    def __init__(
        self,
        scraper: "Scraper",
        credential_store: "CredentialStore | None" = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._scraper = scraper
        self._credential_store = credential_store
        self._is_running = False
        self._is_refreshing = False

        # Periyodik zamanlayıcı
        self._timer = QTimer(self)
        self._timer.setInterval(DEFAULT_REFRESH_INTERVAL_MS)
        self._timer.timeout.connect(self.refresh_now)

        # Aktif thread/worker referansları (GC'den korumak için)
        self._thread: QThread | None = None
        self._worker: _ScraperWorker | None = None

    # ------------------------------------------------------------------
    # Genel durum
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """Yenileme döngüsünün aktif olup olmadığını döner."""
        return self._is_running

    def set_interval(self, seconds: int) -> None:
        """
        Yenileme aralığını saniye cinsinden ayarlar.
        Döngü çalışıyorsa zamanlayıcıyı yeniden başlatır.
        """
        ms = max(1, seconds) * 1000  # minimum 1 saniye
        self._timer.setInterval(ms)
        if self._is_running:
            self._timer.start()  # aralığı anında uygula

    # ------------------------------------------------------------------
    # Döngü kontrolü
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Periyodik yenileme döngüsünü başlatır ve hemen ilk yenilemeyi tetikler."""
        if self._is_running:
            return
        self._is_running = True
        self._timer.start()
        self.refresh_now()

    def stop(self) -> None:
        """Periyodik yenileme döngüsünü durdurur."""
        self._is_running = False
        self._timer.stop()

    # ------------------------------------------------------------------
    # Yenileme
    # ------------------------------------------------------------------

    def refresh_now(self) -> None:
        """Scraping işlemini hemen başlatır."""
        if self._is_refreshing:
            return
        self._is_refreshing = True
        self.refresh_started.emit()
        # Selenium thread-safe olmadığı için main thread'de çalıştır
        # UI kısa süre bloke olabilir ama crash olmaz
        try:
            villages = self._scraper.fetch_villages()
            self._on_worker_finished(villages)
        except Exception as exc:
            self._on_worker_error(exc)

    def _start_worker_thread(self) -> None:
        """Worker thread'i oluşturur ve başlatır."""
        thread = QThread()
        worker = _ScraperWorker(self._scraper)
        worker.moveToThread(thread)

        # Bağlantılar
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # Referansları sakla
        self._thread = thread
        self._worker = worker

        thread.start()

    # ------------------------------------------------------------------
    # Worker sonuç işleyicileri
    # ------------------------------------------------------------------

    def _on_worker_finished(self, villages: list[VillageData]) -> None:
        """Scraping başarıyla tamamlandığında çağrılır."""
        self._is_refreshing = False
        totals = self.calculate_totals(villages)
        self.data_updated.emit(villages, totals)
        self.refresh_finished.emit(datetime.now())

    def _on_worker_error(self, exc: Exception) -> None:
        """Scraping hatası oluştuğunda çağrılır."""
        import logging, traceback
        self._is_refreshing = False
        logging.error(f"Scraper worker hatası: {type(exc).__name__}: {exc}\n{traceback.format_exc()}")

        if isinstance(exc, SessionExpiredError):
            self._handle_session_expired()
        else:
            self.error_occurred.emit(str(exc))

    # ------------------------------------------------------------------
    # Oturum yenileme
    # ------------------------------------------------------------------

    def _handle_session_expired(self) -> None:
        """
        Oturum süresi dolduğunda tarayıcı çerezlerini yeniden yüklemeyi dener.
        Başarısız olursa error_occurred sinyali yayınlar.
        """
        try:
            self._scraper.reload_cookies()
            if self._scraper.is_logged_in():
                self.refresh_now()
            else:
                self.error_occurred.emit(
                    "Tarayıcı oturumu bulunamadı. Lütfen tarayıcıda oyuna giriş yapın."
                )
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(
                f"Çerez yenileme başarısız: {exc}. Lütfen tarayıcıda oyuna giriş yapın."
            )

    # ------------------------------------------------------------------
    # Hesaplama
    # ------------------------------------------------------------------

    def calculate_totals(self, villages: list[VillageData]) -> ResourceTotals:
        """
        Köy listesindeki tüm kaynakları toplayarak ResourceTotals döner.

        Args:
            villages: VillageData nesnelerinden oluşan liste.

        Returns:
            Tüm köylerin kaynak toplamlarını içeren ResourceTotals nesnesi.
        """
        wood = sum(v.wood for v in villages)
        clay = sum(v.clay for v in villages)
        iron = sum(v.iron for v in villages)
        food = sum(v.food for v in villages)
        return ResourceTotals(wood=wood, clay=clay, iron=iron, food=food)
