# 🤠 Wildguns Kaynak Takip

Wildguns oyunundaki köy kaynaklarını otomatik takip eden, hedef belirleme ve alarm özellikli masaüstü uygulaması.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green?logo=qt)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-orange?logo=selenium)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

---

## 📸 Ekran Görüntüsü

![screenshot](assets/screenshot.png)

---

## ✨ Özellikler

- **Otomatik kaynak takibi** — Belirlediğin aralıkta köy kaynaklarını otomatik çeker
- **Çoklu köy desteği** — Tüm köylerin Odun, Kil, Demir, Yiyecek değerlerini tek tabloda gösterir
- **Genel toplam** — Her köy ve tüm köylerin genel toplamı ayrı sütunda görünür
- **Hedef & Alarm** — Bina upgrade maliyetini gir, hedefe ulaşınca sesli alarm çalar ve popup çıkar
- **İki alarm modu** — Genel toplam hedefine göre veya kaynak kaynak takiple alarm
- **Log sekmesi** — Hataları uygulama içinde görüntüle, crash sonrası log dosyasına yazar
- **Sistem temasından bağımsız** — Dark mode UI, her bilgisayarda aynı görünür

---

## 🚀 Kurulum (Kullanıcılar için)

1. [Releases](https://github.com/furkan-altun/wildguns-tracker/releases) sayfasından `WildgunsTracker.exe` dosyasını indir
2. Exe'yi çalıştır — Python veya başka bir şey yüklemeye gerek yok
3. Açılan Chrome penceresinde oyuna giriş yap
4. **Bağlan** butonuna bas, hazır!

> **Not:** İlk çalıştırmada ChromeDriver otomatik indirilir, internet bağlantısı gereklidir.

---

## 🛠️ Geliştirici Kurulumu

### Gereksinimler

- Python 3.10+
- Google Chrome

### Adımlar

```bash
git clone https://github.com/furkan-altun/wildguns-tracker.git
cd wildguns-tracker
pip install -r requirements.txt
python run.py
```

### Build (EXE oluşturma)

```bash
python -m PyInstaller wildguns.spec --noconfirm
```

Çıktı: `dist/WildgunsTracker.exe`

---

## 📖 Kullanım

### Temel Kullanım

| Buton | Açıklama |
|-------|----------|
| ▶ Otomatik Başlat | Belirlenen aralıkta otomatik veri çekmeye başlar |
| ■ Durdur | Otomatik yenilemeyi durdurur |
| 🔍 Analiz Et | Tek seferlik manuel veri çeker |

**Aralık** alanına saniye cinsinden yenileme sıklığını gir (örn. `30` = 30 saniyede bir).

### Hedef & Alarm

1. **Alarm modunu seç:**
   - *Genel toplam hedefine göre* — Tüm kaynakların toplamı girilen sayıya ulaşınca alarm çalar
   - *Kaynak toplamına göre* — Odun/Kil/Demir/Yiyecek alanlarına bina maliyetini gir, toplam hedefe ulaşınca alarm çalar

2. Hedefe ulaşınca:
   - Sesli alarm tekrar tekrar çalar
   - Ekrana popup çıkar
   - **Tamam** butonuna basınca alarm durur ve otomatik analiz kapanır

### Log Sekmesi

Hata oluştuğunda **📋 Log ⚠** sekmesi işaretlenir. Sekmeye tıklayarak hata detayını görebilirsin.

Crash sonrası log dosyası:
```
C:\Users\[kullanıcı]\AppData\Local\WildgunsTracker\app.log
```

---

## 🔧 Nasıl Çalışır?

Uygulama, Selenium aracılığıyla mevcut Chrome oturumuna bağlanır. Chrome remote debugging modunda açılır, oyun sayfasındaki köy tablosu parse edilerek kaynak verileri çekilir. Cloudflare bypass veya şifre gerekmez — kendi Chrome profilin kullanılır.

---

## 📁 Proje Yapısı

```
wildguns-tracker/
├── src/
│   ├── main.py              # Uygulama giriş noktası
│   ├── main_window.py       # Ana pencere UI
│   ├── scraper.py           # Selenium ile veri çekme
│   ├── resource_tracker.py  # Zamanlayıcı & veri yönetimi
│   ├── alarm_manager.py     # Ses & alarm kontrolü
│   ├── models.py            # Veri modelleri
│   ├── settings_store.py    # Ayar kalıcılığı
│   └── login_dialog.py      # Chrome bağlantı diyalogu
├── assets/
│   └── alarm.wav            # Alarm sesi
├── run.py                   # Başlatıcı
├── wildguns.spec            # PyInstaller build konfigürasyonu
└── requirements.txt
```

---

## 📄 Lisans

MIT License — dilediğin gibi kullanabilirsin.
