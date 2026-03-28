"""
Wildguns oyun sitesinden köy kaynak verilerini çeken Scraper bileşeni.

Selenium ile mevcut Chrome oturumuna bağlanır.
Cloudflare bypass, çerez yönetimi otomatik — kullanıcı sadece
Chrome'u remote debugging modunda açmalıdır.
"""
from __future__ import annotations

import re
import subprocess
import time

from bs4 import BeautifulSoup

from src.models import VillageData
from src.exceptions import (
    NetworkError,
    ParseError,
    SessionExpiredError,
)

OVERVIEW_URL = "https://s1-tr.wildguns.gameforge.com/user.php?action=overview&view=over"
REMOTE_DEBUG_PORT = 9222


class Scraper:
    """
    Selenium ile mevcut Chrome oturumuna bağlanarak köy verilerini çeken sınıf.
    """

    def __init__(self) -> None:
        self._driver = None

    def set_cookies_from_string(self, cookie_str: str) -> None:
        """Uyumluluk için — Selenium modunda kullanılmaz."""
        pass

    def reload_cookies(self) -> None:
        """Selenium oturumu yeniden bağlanır."""
        self._connect_driver()

    def launch_chrome(self) -> None:
        """Chrome'u remote debugging modunda otomatik başlatır."""
        import os
        import time

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
        ]
        chrome = next((p for p in chrome_paths if os.path.exists(p)), None)
        if not chrome:
            return  # bulunamazsa dialog'dan manuel başlatılır

        # Zaten açıksa tekrar açma
        if self.is_logged_in():
            return

        profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "WildgunsTracker", "ChromeProfile")
        os.makedirs(profile_dir, exist_ok=True)

        subprocess.Popen([
            chrome,
            f"--remote-debugging-port={REMOTE_DEBUG_PORT}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "https://s1-tr.wildguns.gameforge.com",
        ])

        # Chrome'un açılmasını bekle (max 8 saniye)
        for _ in range(16):
            time.sleep(0.5)
            if self.is_logged_in():
                break

    def is_logged_in(self) -> bool:
        """Chrome remote debugging portuna bağlanılabiliyor mu kontrol eder."""
        try:
            import urllib.request
            urllib.request.urlopen(f"http://localhost:{REMOTE_DEBUG_PORT}/json", timeout=2)
            return True
        except Exception:
            return False

    def _connect_driver(self) -> None:
        """Mevcut Chrome oturumuna bağlanır."""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None

        options = Options()
        options.add_experimental_option("debuggerAddress", f"localhost:{REMOTE_DEBUG_PORT}")
        options.add_argument("--no-sandbox")

        try:
            self._driver = webdriver.Chrome(options=options)
        except Exception as exc:
            raise NetworkError(
                f"Chrome'a bağlanılamadı. Chrome'un remote debugging modunda açık olduğundan emin olun.\n"
                f"Hata: {exc}"
            ) from exc

    def fetch_villages(self) -> list[VillageData]:
        """
        Köy genel durum sayfasını Selenium ile açarak tüm köylerin verilerini döner.
        """
        if not self.is_logged_in():
            raise SessionExpiredError(
                f"Chrome remote debugging portu ({REMOTE_DEBUG_PORT}) bulunamadı.\n"
                "Lütfen Chrome'u remote debugging modunda başlatın."
            )

        if self._driver is None:
            self._connect_driver()

        try:
            self._driver.get(OVERVIEW_URL)
            time.sleep(1.5)  # sayfa yüklenmesi için bekle
            html = self._driver.page_source
        except Exception as exc:
            self._driver = None
            raise NetworkError(f"Sayfa yüklenemedi: {exc}") from exc

        return self._parse_villages(html)

    def _parse_villages(self, html: str) -> list[VillageData]:
        soup = BeautifulSoup(html, "html.parser")

        if self._is_login_page(soup):
            raise SessionExpiredError(
                "Oturum süresi dolmuş. Lütfen Chrome'da oyuna tekrar giriş yapın."
            )

        table = self._find_village_table(soup)
        if table is None:
            raise ParseError(
                "'Köy Genel Durum' tablosu bulunamadı. "
                "Chrome'da 'Köy genel durum' sekmesini açın."
            )

        return self._extract_village_rows(table)

    def _is_login_page(self, soup: BeautifulSoup) -> bool:
        if soup.find("form", attrs={"action": re.compile(r"action=login", re.I)}):
            return True
        if soup.find("input", attrs={"name": "pass"}):
            return True
        return False

    def _find_village_table(self, soup: BeautifulSoup):
        """switchvillage linki içeren tabloyu bulur."""
        for table in soup.find_all("table"):
            if table.find("a", href=re.compile(r"switchvillage=")):
                return table
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) >= 2:
                text = table.get_text(separator=" ", strip=True).lower()
                if "köy" in text or "village" in text:
                    return table
        return None

    def _extract_village_rows(self, table) -> list[VillageData]:
        villages: list[VillageData] = []
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 6:
                continue
            if cells[0].name == "th" or row.find("th"):
                continue

            try:
                name = cells[0].get_text(strip=True)
                if not name:
                    continue

                wood = self._parse_resource(cells[1].get_text(strip=True))
                clay = self._parse_resource(cells[2].get_text(strip=True))
                iron = self._parse_resource(cells[3].get_text(strip=True))
                food = self._parse_resource(cells[5].get_text(strip=True))

                villages.append(VillageData(
                    name=name, wood=wood, clay=clay, iron=iron, food=food,
                ))
            except (ValueError, IndexError):
                continue

        if not villages:
            raise ParseError(
                "Tabloda geçerli köy satırı bulunamadı. "
                "Chrome'da 'Köy genel durum' sekmesini açın."
            )

        return villages

    @staticmethod
    def _parse_resource(text: str) -> int:
        cleaned = re.sub(r"[.,\s]", "", text)
        digits = re.search(r"\d+", cleaned)
        if not digits:
            raise ValueError(f"Sayısal değer bulunamadı: {text!r}")
        return int(digits.group())
