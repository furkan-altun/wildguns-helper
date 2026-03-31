# 🤠 Wildguns Helper

---

## 🌐 Dil / Language

- [🇹🇷 Türkçe](#-türkçe)
- [🇬🇧 English](#-english)

---

## 🇹🇷 Türkçe

Wildguns oyunundaki köy kaynaklarını otomatik takip eden, hedef belirleme ve alarm özellikli tarayıcı scripti.

Tampermonkey userscript olarak çalışır — masaüstü ve mobil tarayıcılarda desteklenir.

### ✨ Özellikler

- Köy kaynaklarını (Odun, Kil, Demir, Yiyecek) otomatik çeker ve tabloda gösterir
- Çoklu köy desteği, genel toplam hesaplama
- Otomatik periyodik yenileme (ayarlanabilir aralık)
- Hedef & Alarm sistemi — hedefe ulaşınca sesli bildirim
- İki alarm modu: Genel toplam veya kaynak bazlı
- **Dil seçici** — panel üzerinden TR / EN arasında geçiş yapılabilir
- Dark mode arayüz, sürüklenebilir panel
- Ayarlar tarayıcı kapatılsa bile korunur

---

### 🚀 Kurulum

#### 1. Tampermonkey'i Yükle

| Platform | İndirme Linki |
|---|---|
| Chrome / Edge (Masaüstü) | [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo) |
| Firefox (Masaüstü) | [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/tampermonkey/) |
| Safari (Masaüstü) | [App Store](https://apps.apple.com/app/tampermonkey/id1482490089) |
| Android (Firefox) | Firefox'u indir → [Tampermonkey](https://addons.mozilla.org/firefox/addon/tampermonkey/) |
| iOS (Safari) | App Store → **Userscripts** uygulamasını indir (ücretsiz) |

---

#### 2. Chrome / Edge için Ek Ayar (Zorunlu)

Chrome ve Edge'de Tampermonkey'in script çalıştırabilmesi için iki ayar açılmalıdır:

1. Tarayıcı adres çubuğuna yaz: `chrome://extensions`
2. Sağ üstteki **"Developer mode"** (Geliştirici modu) anahtarını **Açık** yap
3. Tampermonkey'i bul → **Detaylar** butonuna tıkla
4. **"Allow User Scripts"** seçeneğini **Açık** yap

> ⚠️ Her iki adım da yapılmazsa script çalışmaz.

---

#### 3. Scripti Yükle

Aşağıdaki linke tıkla — Tampermonkey otomatik kurulum ekranını açacak:

**[⬇️ Wildguns Helper'ı Yükle](https://raw.githubusercontent.com/furkan-altun/wildguns-helper/main/wildguns-tracker.user.js)**

Açılan ekranda **"Install"** butonuna bas.

---

#### 4. Kullanım

1. [Wildguns oyun sayfasını](https://s1-tr.wildguns.gameforge.com) aç
2. Sağ üstte **🤠 Wildguns Kaynak Takip** paneli otomatik açılır
3. **▶ Otomatik Başlat** butonuna bas
4. Aralık alanına yenileme sıklığını saniye cinsinden gir (örn. `30`)

---

### 📱 Mobil Kurulum

#### Android

**Firefox ile (Önerilen):**
1. [Firefox for Android](https://play.google.com/store/apps/details?id=org.mozilla.firefox) indir
2. Firefox → Ayarlar → Eklentiler → Tampermonkey'i yükle
3. Yukarıdaki script linkine git → Install

**Kiwi Browser ile:**
1. [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser) indir
2. Chrome Web Store'dan Tampermonkey'i yükle
3. Yukarıdaki script linkine git → Install

#### iOS (iPhone / iPad)

1. App Store'dan **[Userscripts](https://apps.apple.com/app/userscripts/id1463298887)** uygulamasını indir (ücretsiz)
2. **Ayarlar → Safari → Uzantılar → Userscripts → Aç**
3. Userscripts uygulamasını aç → **+** butonuna bas
4. Script URL'ini yapıştır:
   ```
   https://raw.githubusercontent.com/furkan-altun/wildguns-helper/main/wildguns-tracker.user.js
   ```
5. Safari'de Wildguns sayfasını aç

---

### 🔧 Panel Kontrolleri

| Buton / Alan | Açıklama |
|---|---|
| **[TR]** / **[EN]** | Arayüz dilini Türkçe veya İngilizce olarak değiştirir |
| ▶ Otomatik Başlat | Belirlenen aralıkta otomatik veri çekmeye başlar |
| ■ Durdur | Otomatik yenilemeyi durdurur |
| 🔍 Şimdi Yenile | Tek seferlik manuel veri çeker |
| Aralık (sn) | Otomatik yenileme sıklığını saniye cinsinden belirler |
| − | Paneli küçültür |
| ✕ | Paneli kapatır |

---

### 🎯 Alarm Yapılandırması

#### Genel Toplam Modu
Tüm köylerin toplam kaynağı girilen sayıya ulaşınca alarm çalar.

1. **Genel Toplam** seçeneğini seç
2. Hedef alanına bina maliyetini gir (örn. `15000`)
3. Otomatik yenilemeyi başlat

#### Kaynak Bazlı Mod
4 kaynak için ayrı ayrı miktar gir — toplamları hedefe ulaşınca alarm çalar.

1. **Kaynak Bazlı** seçeneğini seç
2. Odun, Kil, Demir, Yiyecek alanlarına bina maliyetlerini gir
3. Otomatik yenilemeyi başlat

Hedefe ulaşınca:
- Sesli alarm çalar
- Ekranda popup çıkar
- Otomatik yenileme durur

---

### 🌍 Dil Seçici

Panel başlığının sağ tarafında **[TR]** ve **[EN]** butonları bulunur. Aktif dil butonu vurgulanmış olarak görünür. Dil tercihi tarayıcı kapatılsa bile korunur — bir sonraki ziyarette aynı dil otomatik yüklenir.

---

## 🇬🇧 English

A browser script that automatically tracks village resources in the Wildguns game, with target setting and alarm features.

Works as a Tampermonkey userscript — supported on desktop and mobile browsers.

### ✨ Features

- Automatically fetches and displays village resources (Wood, Clay, Iron, Food) in a table
- Multi-village support with grand total calculation
- Automatic periodic refresh (configurable interval)
- Target & Alarm system — audio notification when target is reached
- Two alarm modes: Grand Total or Per Resource
- **Language selector** — switch between TR / EN directly from the panel
- Dark mode interface, draggable panel
- Settings are preserved even after closing the browser

---

### 🚀 Installation

#### 1. Install Tampermonkey

| Platform | Download Link |
|---|---|
| Chrome / Edge (Desktop) | [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo) |
| Firefox (Desktop) | [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/tampermonkey/) |
| Safari (Desktop) | [App Store](https://apps.apple.com/app/tampermonkey/id1482490089) |
| Android (Firefox) | Download Firefox → [Tampermonkey](https://addons.mozilla.org/firefox/addon/tampermonkey/) |
| iOS (Safari) | App Store → Download **Userscripts** app (free) |

---

#### 2. Extra Step for Chrome / Edge (Required)

Chrome and Edge require two additional settings to allow Tampermonkey to run scripts:

1. Type in the address bar: `chrome://extensions`
2. Enable **"Developer mode"** toggle in the top right corner
3. Find Tampermonkey → click **Details**
4. Enable **"Allow User Scripts"**

> ⚠️ Both steps are required, otherwise the script will not run.

---

#### 3. Install the Script

Click the link below — Tampermonkey will open the installation screen automatically:

**[⬇️ Install Wildguns Helper](https://raw.githubusercontent.com/furkan-altun/wildguns-helper/main/wildguns-tracker.user.js)**

Click the **"Install"** button on the screen that opens.

---

#### 4. Usage

1. Open the [Wildguns game page](https://s1-tr.wildguns.gameforge.com)
2. The **🤠 Wildguns Resource Tracker** panel opens automatically in the top right
3. Click the **▶ Auto Start** button
4. Enter the refresh frequency in seconds in the interval field (e.g. `30`)

---

### 📱 Mobile Installation

#### Android

**With Firefox (Recommended):**
1. Download [Firefox for Android](https://play.google.com/store/apps/details?id=org.mozilla.firefox)
2. Firefox → Settings → Add-ons → Install Tampermonkey
3. Go to the script link above → Install

**With Kiwi Browser:**
1. Download [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser)
2. Install Tampermonkey from the Chrome Web Store
3. Go to the script link above → Install

#### iOS (iPhone / iPad)

1. Download **[Userscripts](https://apps.apple.com/app/userscripts/id1463298887)** from the App Store (free)
2. **Settings → Safari → Extensions → Userscripts → Enable**
3. Open the Userscripts app → tap the **+** button
4. Paste the script URL:
   ```
   https://raw.githubusercontent.com/furkan-altun/wildguns-helper/main/wildguns-tracker.user.js
   ```
5. Open the Wildguns page in Safari

---

### 🔧 Panel Controls

| Button / Field | Description |
|---|---|
| **[TR]** / **[EN]** | Switches the interface language between Turkish and English |
| ▶ Auto Start | Starts automatic data fetching at the configured interval |
| ■ Stop | Stops automatic refresh |
| 🔍 Refresh Now | Fetches data once manually |
| Interval (sec) | Sets the automatic refresh frequency in seconds |
| − | Minimizes the panel |
| ✕ | Closes the panel |

---

### 🎯 Alarm Configuration

#### Grand Total Mode
The alarm triggers when the combined resources of all villages reach the entered number.

1. Select the **Grand Total** option
2. Enter the building cost in the target field (e.g. `15000`)
3. Start automatic refresh

#### Per Resource Mode
Enter separate amounts for each of the 4 resources — the alarm triggers when their totals reach the targets.

1. Select the **Per Resource** option
2. Enter building costs in the Wood, Clay, Iron, Food fields
3. Start automatic refresh

When the target is reached:
- An audio alarm sounds
- A popup appears on screen
- Automatic refresh stops

---

### 🌍 Language Selector

The **[TR]** and **[EN]** buttons are located on the right side of the panel header. The active language button is highlighted. Your language preference is preserved even after closing the browser — the same language loads automatically on your next visit.

---

## 📄 License

MIT License
