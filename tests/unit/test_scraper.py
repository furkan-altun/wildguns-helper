"""
Scraper sınıfı için birim testleri.

Gerçek HTTP bağlantısı gerektirmeyen, HTML ayrıştırma ve oturum
mantığını test eden testler.
"""

import pytest
from src.scraper import Scraper
from src.models import VillageData
from src.exceptions import (
    AuthenticationError,
    NetworkError,
    ParseError,
    SessionExpiredError,
)


# ---------------------------------------------------------------------------
# Yardımcı HTML oluşturucular
# ---------------------------------------------------------------------------

def make_village_table_html(*rows: tuple) -> str:
    """
    Verilen köy satırlarından "Köy Genel Durum" tablosu içeren HTML üretir.

    Her row: (name, wood, clay, iron, storage, food)
    """
    tr_rows = ""
    for name, wood, clay, iron, storage, food in rows:
        tr_rows += (
            f"<tr>"
            f"<td>{name}</td>"
            f"<td>{wood}</td>"
            f"<td>{clay}</td>"
            f"<td>{iron}</td>"
            f"<td>{storage}</td>"
            f"<td>{food}</td>"
            f"</tr>"
        )
    return f"""
    <html><body>
    <table>
      <tr><th>Köy İsmi</th><th>Odun</th><th>Kil</th><th>Demir</th><th>Depo</th><th>Yiyecek</th></tr>
      {tr_rows}
    </table>
    </body></html>
    """


def make_login_page_html() -> str:
    """Giriş formu içeren HTML döner."""
    return """
    <html><body>
    <form action="user.php?action=login" method="post">
      <input type="text" name="login" />
      <input type="password" name="pass" />
      <button type="submit">Giriş Yap</button>
    </form>
    </body></html>
    """


# ---------------------------------------------------------------------------
# is_logged_in testleri
# ---------------------------------------------------------------------------

class TestIsLoggedIn:
    def test_returns_false_when_no_cookie(self):
        scraper = Scraper()
        assert scraper.is_logged_in() is False

    def test_returns_true_when_session_cookie_set(self):
        scraper = Scraper()
        scraper._session.cookies.set("wg_sid", "abc123", domain="tr.wildguns.gameforge.com")
        assert scraper.is_logged_in() is True


# ---------------------------------------------------------------------------
# _parse_resource testleri
# ---------------------------------------------------------------------------

class TestParseResource:
    def test_plain_integer(self):
        assert Scraper._parse_resource("131") == 131

    def test_integer_with_dot_separator(self):
        assert Scraper._parse_resource("1.234") == 1234

    def test_integer_with_comma_separator(self):
        assert Scraper._parse_resource("2,600") == 2600

    def test_integer_with_spaces(self):
        assert Scraper._parse_resource("1 500") == 1500

    def test_zero(self):
        assert Scraper._parse_resource("0") == 0

    def test_raises_on_non_numeric(self):
        with pytest.raises(ValueError):
            Scraper._parse_resource("abc")

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError):
            Scraper._parse_resource("")


# ---------------------------------------------------------------------------
# _parse_villages testleri
# ---------------------------------------------------------------------------

class TestParseVillages:
    def test_single_village_parsed_correctly(self):
        html = make_village_table_html(("Beşiktaş", 131, 145, 131, 2600, 97))
        scraper = Scraper()
        villages = scraper._parse_villages(html)

        assert len(villages) == 1
        v = villages[0]
        assert v.name == "Beşiktaş"
        assert v.wood == 131
        assert v.clay == 145
        assert v.iron == 131
        assert v.food == 97

    def test_multiple_villages_parsed(self):
        html = make_village_table_html(
            ("Beşiktaş", 131, 145, 131, 2600, 97),
            ("OrkunKokcu", 80, 80, 80, 2600, 655),
        )
        scraper = Scraper()
        villages = scraper._parse_villages(html)

        assert len(villages) == 2
        assert villages[0].name == "Beşiktaş"
        assert villages[1].name == "OrkunKokcu"

    def test_storage_column_is_skipped(self):
        """Depo kapasitesi (sütun 4) yiyecek olarak alınmamalı."""
        html = make_village_table_html(("TestKöy", 10, 20, 30, 9999, 50))
        scraper = Scraper()
        villages = scraper._parse_villages(html)

        assert villages[0].food == 50  # 9999 değil

    def test_raises_session_expired_on_login_page(self):
        scraper = Scraper()
        with pytest.raises(SessionExpiredError):
            scraper._parse_villages(make_login_page_html())

    def test_raises_parse_error_when_no_table(self):
        scraper = Scraper()
        with pytest.raises(ParseError):
            scraper._parse_villages("<html><body><p>Boş sayfa</p></body></html>")

    def test_raises_parse_error_when_table_has_no_valid_rows(self):
        """Tablo var ama geçerli veri satırı yok."""
        html = """
        <html><body>
        <table>
          <tr><th>Köy İsmi</th><th>Odun</th></tr>
        </table>
        </body></html>
        """
        scraper = Scraper()
        with pytest.raises(ParseError):
            scraper._parse_villages(html)

    def test_returns_village_data_instances(self):
        html = make_village_table_html(("Köy1", 100, 200, 300, 1000, 400))
        scraper = Scraper()
        villages = scraper._parse_villages(html)

        assert all(isinstance(v, VillageData) for v in villages)


# ---------------------------------------------------------------------------
# fetch_villages — oturum kontrolü testi (Gereksinim 1.5)
# ---------------------------------------------------------------------------

class TestFetchVillagesSessionCheck:
    def test_raises_session_expired_when_not_logged_in(self):
        """
        Oturum çerezi olmadan fetch_villages() çağrıldığında
        SessionExpiredError fırlatılmalıdır. (Gereksinim 1.5)
        """
        scraper = Scraper()
        # Çerez yok → is_logged_in() False döner
        with pytest.raises(SessionExpiredError):
            scraper.fetch_villages()
