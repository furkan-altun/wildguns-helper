"""
SettingsStore birim testleri.
Gereksinimler: 4.1, 4.2, 4.3, 4.5
"""
import pytest
from unittest.mock import MagicMock, patch

from src.settings_store import SettingsStore, RESOURCES


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Her test için izole QSettings kullanan SettingsStore."""
    with patch("src.settings_store.QSettings") as MockQSettings:
        mock_settings = MagicMock()
        _data: dict[str, object] = {}

        def mock_value(key, defaultValue=None):
            return _data.get(key, defaultValue)

        def mock_set_value(key, value):
            _data[key] = value

        mock_settings.value.side_effect = mock_value
        mock_settings.setValue.side_effect = mock_set_value
        mock_settings.sync.return_value = None
        MockQSettings.return_value = mock_settings

        yield SettingsStore()


class TestSettingsStore:
    def test_resources_list(self):
        assert set(RESOURCES) == {"wood", "clay", "iron", "food"}

    def test_get_threshold_returns_none_by_default(self, store):
        for resource in RESOURCES:
            assert store.get_threshold(resource) is None

    def test_set_and_get_threshold(self, store):
        store.set_threshold("wood", 5000)
        assert store.get_threshold("wood") == 5000

    def test_set_threshold_to_none_disables_it(self, store):
        store.set_threshold("clay", 1000)
        store.set_threshold("clay", None)
        assert store.get_threshold("clay") is None

    def test_set_threshold_zero_is_valid(self, store):
        store.set_threshold("iron", 0)
        assert store.get_threshold("iron") == 0

    def test_get_all_thresholds_returns_all_resources(self, store):
        result = store.get_all_thresholds()
        assert set(result.keys()) == set(RESOURCES)

    def test_get_all_thresholds_default_all_none(self, store):
        result = store.get_all_thresholds()
        for resource in RESOURCES:
            assert result[resource] is None

    def test_get_all_thresholds_reflects_set_values(self, store):
        store.set_threshold("wood", 100)
        store.set_threshold("food", 200)
        result = store.get_all_thresholds()
        assert result["wood"] == 100
        assert result["food"] == 200
        assert result["clay"] is None
        assert result["iron"] is None

    def test_thresholds_are_independent_per_resource(self, store):
        store.set_threshold("wood", 1000)
        store.set_threshold("clay", 2000)
        assert store.get_threshold("wood") == 1000
        assert store.get_threshold("clay") == 2000
        assert store.get_threshold("iron") is None
