"""Debug: Sayfanın HTML'ini ve tablo yapısını inceler."""
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

OVERVIEW_URL = "https://s1-tr.wildguns.gameforge.com/user.php?action=overview&view=over"

options = Options()
options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=options)

driver.get(OVERVIEW_URL)
time.sleep(2)
html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

# switchvillage linki içeren tabloyu bul
for table in soup.find_all("table"):
    if table.find("a", href=lambda h: h and "switchvillage=" in h):
        print("=== TABLO BULUNDU ===")
        rows = table.find_all("tr")
        for i, row in enumerate(rows[:5]):  # ilk 5 satır
            cells = row.find_all(["td", "th"])
            print(f"\nSatır {i} ({len(cells)} hücre):")
            for j, cell in enumerate(cells):
                print(f"  [{j}] {cell.get_text(strip=True)[:40]!r}")
        break
else:
    print("Tablo bulunamadı!")
    # Tüm tabloları listele
    for i, t in enumerate(soup.find_all("table")):
        print(f"Tablo {i}: {t.get_text(separator=' ', strip=True)[:80]}")
