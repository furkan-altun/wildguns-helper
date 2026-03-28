"""
CredentialStore birim testleri.
"""
import pytest
from src.credential_store import CredentialStore


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Her test için geçici dizin kullanan CredentialStore."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    return CredentialStore()


class TestCredentialStore:
    def test_service_name_constant(self):
        assert CredentialStore.SERVICE_NAME == "wildguns-tracker"

    def test_load_returns_none_when_empty(self, store):
        assert store.load() is None

    def test_save_and_load_returns_cookie_string(self, store):
        long_cookie = "WildGuns-Game=abc123; wildgunsreborn=xyz; PHPSESSID=def456; " + "x=" * 500
        store.save(long_cookie)
        result = store.load()
        assert result is not None
        assert result[0] == long_cookie

    def test_save_overwrites_existing(self, store):
        store.save("cookie1=a")
        store.save("cookie2=b")
        result = store.load()
        assert result[0] == "cookie2=b"

    def test_delete_removes_data(self, store):
        store.save("cookie=abc")
        store.delete()
        assert store.load() is None

    def test_delete_on_empty_does_not_raise(self, store):
        store.delete()  # hata fırlatmamalı

    def test_load_returns_tuple(self, store):
        store.save("cookie=abc")
        result = store.load()
        assert isinstance(result, tuple)
        assert len(result) == 2
