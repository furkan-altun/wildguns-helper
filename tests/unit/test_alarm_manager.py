"""
AlarmManager sınıfı için birim testleri.

PyQt6 sinyalleri test edilirken QApplication gerektiren durumlar için
unittest.mock kullanılır.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from src.models import ResourceTotals


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
# Fixture: QApplication + AlarmManager
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    """Modül kapsamında tek bir QApplication örneği oluşturur."""
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def alarm_manager(qapp):
    """Her test için temiz bir AlarmManager örneği döner."""
    from src.alarm_manager import AlarmManager
    manager = AlarmManager()
    # Ses çalmayı devre dışı bırak (test ortamında ses sistemi olmayabilir)
    manager._sound_loaded = False
    return manager


# ---------------------------------------------------------------------------
# Yardımcı: totals ve thresholds oluşturucular
# ---------------------------------------------------------------------------

def make_totals(**kwargs) -> ResourceTotals:
    defaults = {"wood": 0, "clay": 0, "iron": 0, "food": 0}
    defaults.update(kwargs)
    return ResourceTotals(**defaults)


def make_thresholds(**kwargs) -> dict:
    """Tüm kaynaklar için None eşik döner; kwargs ile override edilebilir."""
    base = {"wood": None, "clay": None, "iron": None, "food": None}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Test: Eşik None ise alarm tetiklenmez
# ---------------------------------------------------------------------------

class TestNoneThreshold:
    def test_none_threshold_does_not_trigger_alarm(self, alarm_manager):
        """Eşik None ise alarm_triggered sinyali yayınlanmamalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(wood=99999)
        thresholds = make_thresholds(wood=None)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 0

    def test_all_none_thresholds_no_alarm(self, alarm_manager):
        """Tüm eşikler None ise hiç alarm tetiklenmemelidir."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(wood=5000, clay=5000, iron=5000, food=5000)
        thresholds = make_thresholds()  # hepsi None
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 0


# ---------------------------------------------------------------------------
# Test: Toplam >= eşik ise alarm_triggered sinyali yayınlanır
# ---------------------------------------------------------------------------

class TestAlarmTriggered:
    def test_total_equals_threshold_triggers_alarm(self, alarm_manager):
        """Toplam == eşik olduğunda alarm_triggered yayınlanmalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(wood=1000)
        thresholds = make_thresholds(wood=1000)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 1
        assert catcher.calls[0] == ("wood", 1000)

    def test_total_exceeds_threshold_triggers_alarm(self, alarm_manager):
        """Toplam > eşik olduğunda alarm_triggered yayınlanmalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(clay=2500)
        thresholds = make_thresholds(clay=2000)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 1
        assert catcher.calls[0] == ("clay", 2500)

    def test_alarm_carries_correct_resource_and_amount(self, alarm_manager):
        """Sinyal doğru kaynak adı ve miktarı taşımalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(iron=750)
        thresholds = make_thresholds(iron=500)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.calls[0][0] == "iron"
        assert catcher.calls[0][1] == 750


# ---------------------------------------------------------------------------
# Test: Toplam < eşik ise alarm_triggered sinyali yayınlanmaz
# ---------------------------------------------------------------------------

class TestAlarmNotTriggered:
    def test_total_below_threshold_no_alarm(self, alarm_manager):
        """Toplam < eşik olduğunda alarm_triggered yayınlanmamalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(food=300)
        thresholds = make_thresholds(food=500)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 0

    def test_zero_total_below_threshold_no_alarm(self, alarm_manager):
        """Toplam 0 iken eşik > 0 ise alarm tetiklenmemelidir."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(wood=0)
        thresholds = make_thresholds(wood=100)
        alarm_manager.check_thresholds(totals, thresholds)

        assert catcher.count == 0


# ---------------------------------------------------------------------------
# Test: silence() sonrası aynı kaynak için alarm tekrar tetiklenmez
# ---------------------------------------------------------------------------

class TestSilence:
    def test_silence_prevents_repeat_alarm(self, alarm_manager):
        """silence() çağrıldıktan sonra aynı kaynak için alarm tekrar tetiklenmemelidir."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        totals = make_totals(wood=1000)
        thresholds = make_thresholds(wood=500)

        # İlk kontrol → alarm tetiklenir
        alarm_manager.check_thresholds(totals, thresholds)
        assert catcher.count == 1

        # Sustur
        alarm_manager.silence("wood")
        catcher.reset()

        # İkinci kontrol → alarm tekrar tetiklenmemeli
        alarm_manager.check_thresholds(totals, thresholds)
        assert catcher.count == 0

    def test_silence_emits_alarm_silenced_signal(self, alarm_manager):
        """silence() çağrıldığında alarm_silenced sinyali yayınlanmalıdır."""
        silenced_catcher = SignalCatcher()
        alarm_manager.alarm_silenced.connect(silenced_catcher)

        alarm_manager.silence("clay")

        assert silenced_catcher.count == 1
        assert silenced_catcher.calls[0] == ("clay",)

    def test_silence_only_affects_specified_resource(self, alarm_manager):
        """Bir kaynağı susturmak diğer kaynakların alarmını etkilememelidir."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        # wood'u sustur
        alarm_manager.silence("wood")

        totals = make_totals(wood=1000, iron=800)
        thresholds = make_thresholds(wood=500, iron=500)
        alarm_manager.check_thresholds(totals, thresholds)

        # Sadece iron alarmı tetiklenmeli
        triggered_resources = [call[0] for call in catcher.calls]
        assert "wood" not in triggered_resources
        assert "iron" in triggered_resources


# ---------------------------------------------------------------------------
# Test: Toplam eşiğin altına düşünce susturma sıfırlanır
# ---------------------------------------------------------------------------

class TestSilenceReset:
    def test_silence_resets_when_total_drops_below_threshold(self, alarm_manager):
        """
        Toplam eşiğin altına düştüğünde susturma sıfırlanmalı;
        tekrar eşiğe ulaşınca alarm yeniden tetiklenmelidir.
        """
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        thresholds = make_thresholds(food=500)

        # 1. Eşiğe ulaş → alarm tetiklenir
        alarm_manager.check_thresholds(make_totals(food=600), thresholds)
        assert catcher.count == 1

        # 2. Sustur
        alarm_manager.silence("food")
        catcher.reset()

        # 3. Eşiğin altına düş → susturma sıfırlanır
        alarm_manager.check_thresholds(make_totals(food=200), thresholds)
        assert catcher.count == 0  # alarm yok, sadece sıfırlama

        # 4. Tekrar eşiğe ulaş → alarm yeniden tetiklenmeli
        alarm_manager.check_thresholds(make_totals(food=600), thresholds)
        assert catcher.count == 1

    def test_no_alarm_while_below_threshold_after_silence(self, alarm_manager):
        """Eşiğin altındayken susturma sıfırlanmış olsa bile alarm tetiklenmemelidir."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        thresholds = make_thresholds(clay=1000)

        # Eşiğe ulaş ve sustur
        alarm_manager.check_thresholds(make_totals(clay=1200), thresholds)
        alarm_manager.silence("clay")
        catcher.reset()

        # Eşiğin altına düş
        alarm_manager.check_thresholds(make_totals(clay=500), thresholds)
        assert catcher.count == 0  # hâlâ eşiğin altında, alarm yok

    def test_reset_silence_manual(self, alarm_manager):
        """reset_silence() manuel olarak susturmayı kaldırmalıdır."""
        catcher = SignalCatcher()
        alarm_manager.alarm_triggered.connect(catcher)

        thresholds = make_thresholds(iron=300)
        totals = make_totals(iron=400)

        # Alarm tetikle ve sustur
        alarm_manager.check_thresholds(totals, thresholds)
        alarm_manager.silence("iron")
        catcher.reset()

        # Manuel sıfırla
        alarm_manager.reset_silence("iron")

        # Tekrar kontrol → alarm tetiklenmeli
        alarm_manager.check_thresholds(totals, thresholds)
        assert catcher.count == 1
