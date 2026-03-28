"""
ResourceTracker sınıfı için birim testleri.

QThread ve gerçek HTTP çağrıları mock'lanır.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from src.models import ResourceTotals, VillageData


# ---------------------------------------------------------------------------
# Yardımcı: sinyal yakalayıcı
# ---------------------------------------------------------------------------

class SignalCatcher:
    """Bir Qt sinyalinin yayınlanıp yayınlanmadığını ve argümanlarını kaydeder."""

    def __init__(self):
        self.calls: list[tuple] = []

    def __call__(self, *args):
        self.calls.append(args)

    @property
    def count(self) -> int:
        return len(self.calls)

    def reset(self):
        self.calls.clear()


# ---------------------------------------------------------------------------
# Fixture: QApplication
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# ---------------------------------------------------------------------------
# Fixture: mock Scraper ve CredentialStore
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_scraper():
    scraper = MagicMock()
    scraper.fetch_villages.return_value = [
        VillageData(name="Köy 1", wood=1000, clay=2000, iron=1500, food=500),
        VillageData(name="Köy 2", wood=3000, clay=1000, iron=2500, food=1500),
    ]
    scraper.is_logged_in.return_value = True
    scraper.reload_cookies.return_value = None
    return scraper


@pytest.fixture
def tracker(qapp, mock_scraper):
    """Her test için temiz bir ResourceTracker örneği döner."""
    from src.resource_tracker import ResourceTracker
    rt = ResourceTracker(scraper=mock_scraper)
    yield rt
    rt.stop()


# ---------------------------------------------------------------------------
# Test: calculate_totals() doğru toplamları hesaplar
# ---------------------------------------------------------------------------

class TestCalculateTotals:
    def test_empty_list_returns_zero_totals(self, tracker):
        """Boş liste için tüm toplamlar sıfır olmalıdır."""
        totals = tracker.calculate_totals([])
        assert totals.wood == 0
        assert totals.clay == 0
        assert totals.iron == 0
        assert totals.food == 0

    def test_single_village_totals_equal_village_values(self, tracker):
        """Tek köy için toplamlar köy değerlerine eşit olmalıdır."""
        villages = [VillageData(name="Köy 1", wood=100, clay=200, iron=300, food=400)]
        totals = tracker.calculate_totals(villages)
        assert totals.wood == 100
        assert totals.clay == 200
        assert totals.iron == 300
        assert totals.food == 400

    def test_multiple_villages_sums_correctly(self, tracker):
        """Birden fazla köy için toplamlar aritmetik toplamla eşleşmelidir."""
        villages = [
            VillageData(name="Köy 1", wood=1000, clay=2000, iron=1500, food=500),
            VillageData(name="Köy 2", wood=3000, clay=1000, iron=2500, food=1500),
            VillageData(name="Köy 3", wood=500,  clay=750,  iron=250,  food=100),
        ]
        totals = tracker.calculate_totals(villages)
        assert totals.wood == 4500
        assert totals.clay == 3750
        assert totals.iron == 4250
        assert totals.food == 2100

    def test_returns_resource_totals_instance(self, tracker):
        """Dönen nesne ResourceTotals türünde olmalıdır."""
        result = tracker.calculate_totals([])
        assert isinstance(result, ResourceTotals)

    def test_zero_values_sum_to_zero(self, tracker):
        """Tüm değerleri sıfır olan köyler için toplamlar sıfır olmalıdır."""
        villages = [
            VillageData(name="Köy 1", wood=0, clay=0, iron=0, food=0),
            VillageData(name="Köy 2", wood=0, clay=0, iron=0, food=0),
        ]
        totals = tracker.calculate_totals(villages)
        assert totals.wood == 0
        assert totals.clay == 0
        assert totals.iron == 0
        assert totals.food == 0


# ---------------------------------------------------------------------------
# Test: start() / stop() döngüsü (is_running durumu)
# ---------------------------------------------------------------------------

class TestStartStop:
    def test_initial_state_is_not_running(self, tracker):
        """Başlangıçta is_running False olmalıdır."""
        assert tracker.is_running is False

    def test_start_sets_is_running_true(self, tracker):
        """start() çağrıldıktan sonra is_running True olmalıdır."""
        with patch.object(tracker, "refresh_now"):
            tracker.start()
        assert tracker.is_running is True

    def test_stop_sets_is_running_false(self, tracker):
        """stop() çağrıldıktan sonra is_running False olmalıdır."""
        with patch.object(tracker, "refresh_now"):
            tracker.start()
        tracker.stop()
        assert tracker.is_running is False

    def test_start_stop_cycle(self, tracker):
        """start() → stop() → start() döngüsü doğru çalışmalıdır."""
        with patch.object(tracker, "refresh_now"):
            tracker.start()
            assert tracker.is_running is True
            tracker.stop()
            assert tracker.is_running is False
            tracker.start()
            assert tracker.is_running is True

    def test_double_start_does_not_change_state(self, tracker):
        """İkinci start() çağrısı durumu değiştirmemelidir."""
        with patch.object(tracker, "refresh_now") as mock_refresh:
            tracker.start()
            tracker.start()
        assert tracker.is_running is True
        # refresh_now yalnızca bir kez çağrılmalı
        assert mock_refresh.call_count == 1

    def test_stop_when_not_running_is_safe(self, tracker):
        """Çalışmıyorken stop() çağrısı hata fırlatmamalıdır."""
        assert tracker.is_running is False
        tracker.stop()  # hata fırlatmamalı
        assert tracker.is_running is False


# ---------------------------------------------------------------------------
# Test: refresh_now() çağrıldığında refresh_started sinyali yayınlanır
# ---------------------------------------------------------------------------

class TestRefreshNow:
    def test_refresh_now_emits_refresh_started(self, tracker):
        """refresh_now() çağrıldığında refresh_started sinyali yayınlanmalıdır."""
        catcher = SignalCatcher()
        tracker.refresh_started.connect(catcher)

        # _start_worker_thread'i patch'le; sadece sinyal yayınlanmasını test et
        with patch.object(tracker, "_start_worker_thread"):
            tracker.refresh_now()

        assert catcher.count == 1

    def test_refresh_now_does_not_emit_twice_while_refreshing(self, tracker):
        """Yenileme devam ederken ikinci refresh_now() çağrısı sinyal yayınlamamalıdır."""
        catcher = SignalCatcher()
        tracker.refresh_started.connect(catcher)

        with patch.object(tracker, "_start_worker_thread"):
            tracker.refresh_now()
            tracker.refresh_now()  # is_refreshing=True olduğu için yok sayılmalı

        assert catcher.count == 1


# ---------------------------------------------------------------------------
# Test: SessionExpiredError sonrası çerez yenileme
# ---------------------------------------------------------------------------

class TestSessionExpiredHandling:
    def test_session_expired_reloads_cookies_and_retries(self, tracker, mock_scraper):
        """SessionExpiredError yakalandığında reload_cookies() çağrılmalıdır."""
        mock_scraper.is_logged_in.return_value = True

        with patch.object(tracker, "refresh_now") as mock_refresh:
            tracker._handle_session_expired()

        mock_scraper.reload_cookies.assert_called_once()
        mock_refresh.assert_called_once()

    def test_session_expired_no_cookie_after_reload_emits_error(self, tracker, mock_scraper):
        """Çerez yenileme sonrası hâlâ giriş yoksa error_occurred yayınlanmalıdır."""
        mock_scraper.is_logged_in.return_value = False

        error_catcher = SignalCatcher()
        tracker.error_occurred.connect(error_catcher)

        tracker._handle_session_expired()

        assert error_catcher.count == 1
        assert "tarayıcı" in error_catcher.calls[0][0].lower()

    def test_session_expired_reload_exception_emits_error(self, tracker, mock_scraper):
        """reload_cookies() hata fırlatırsa error_occurred yayınlanmalıdır."""
        mock_scraper.reload_cookies.side_effect = Exception("disk hatası")

        error_catcher = SignalCatcher()
        tracker.error_occurred.connect(error_catcher)

        tracker._handle_session_expired()

        assert error_catcher.count == 1
