# Uygulama Planı: Wildguns Kaynak Takip ve Alarm Uygulaması

## Genel Bakış

Uygulama Python + PyQt6 ile geliştirilecektir. Katmanlı mimari (Veri → İş Mantığı → Sunum) ve Qt sinyal/slot mekanizması temel alınacaktır. Görevler, her adımın bir öncekinin üzerine inşa edildiği artımlı bir sırayla düzenlenmiştir.

## Görevler

- [x] 1. Proje yapısını ve temel veri modellerini oluştur
  - `src/` dizini altında `models.py`, `exceptions.py` dosyalarını oluştur
  - `VillageData`, `ResourceTotals`, `ThresholdConfig`, `AppState` dataclass'larını yaz
  - `TrackerError`, `NetworkError`, `ParseError`, `AuthenticationError`, `SessionExpiredError` hata hiyerarşisini tanımla
  - `tests/unit/`, `tests/property/`, `tests/conftest.py` iskeletini oluştur
  - `requirements.txt` dosyasını oluştur (PyQt6, requests, beautifulsoup4, keyring, hypothesis, pytest)
  - _Gereksinimler: 1.4, 3.1, 3.2, 3.3, 3.4_

- [x] 2. Scraper bileşenini uygula
  - [x] 2.1 `src/scraper.py` dosyasını oluştur ve `Scraper` sınıfını yaz
    - `requests.Session` ile oturum yönetimi
    - `login(username, password) -> bool` metodunu uygula; başarısız olursa `AuthenticationError` fırlat
    - `is_logged_in() -> bool` metodunu uygula; oturum çerezi kontrolü yap
    - `fetch_villages() -> list[VillageData]` metodunu uygula; `NetworkError`, `ParseError`, `SessionExpiredError` fırlat
    - BeautifulSoup4 ile "Köy Genel Durum" tablosunu ayrıştır; köy adı, odun, kil, demir, yiyecek sütunlarını çıkar
    - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 2.2 HTML ayrıştırma round-trip özellik testi yaz
    - **Özellik 1: HTML Ayrıştırma Round-Trip**
    - **Doğrular: Gereksinim 1.1, 1.2, 1.3**
    - `tests/property/test_parsing_properties.py` içine `test_html_parsing_round_trip` yaz
    - Hypothesis `@given` ile rastgele köy listesi üret, HTML tablosu oluştur, ayrıştır, orijinalle karşılaştır

  - [ ]* 2.3 Geçersiz HTML'de hata fırlatma özellik testi yaz
    - **Özellik 2: Geçersiz HTML'de Hata Fırlatma**
    - **Doğrular: Gereksinim 1.4**
    - `test_invalid_html_raises_error` testini yaz; beklenen tablo içermeyen HTML için `ParseError` veya `NetworkError` doğrula

  - [ ]* 2.4 Oturum açılmamış durumda hata fırlatma özellik testi yaz
    - **Özellik 3: Oturum Açılmamış Durumda Hata Fırlatma**
    - **Doğrular: Gereksinim 1.5, 6.2**
    - `test_unauthenticated_raises_error` testini yaz; geçersiz çerezli yanıt için `SessionExpiredError` veya `AuthenticationError` doğrula

  - [ ]* 2.5 Scraper birim testlerini yaz
    - `tests/unit/test_scraper.py` içine oturum açılmamış sayfadan `SessionExpiredError` fırlatılmasını test et
    - _Gereksinimler: 1.5_

- [x] 3. Kontrol noktası — Tüm testlerin geçtiğini doğrula
  - Tüm testlerin geçtiğini doğrula, sorular varsa kullanıcıya sor.

- [x] 4. CredentialStore ve SettingsStore bileşenlerini uygula
  - [x] 4.1 `src/credential_store.py` dosyasını oluştur ve `CredentialStore` sınıfını yaz
    - `keyring` kütüphanesi ile `save(username, password)`, `load() -> tuple | None`, `delete()` metodlarını uygula
    - `SERVICE_NAME = "wildguns-tracker"` sabitini tanımla
    - _Gereksinimler: 6.1, 6.4_

  - [x] 4.2 `src/settings_store.py` dosyasını oluştur ve `SettingsStore` sınıfını yaz
    - `QSettings` ile `get_threshold(resource)`, `set_threshold(resource, value)`, `get_all_thresholds()` metodlarını uygula
    - `None` değeri devre dışı eşiği temsil eder
    - _Gereksinimler: 4.1, 4.2, 4.3, 4.5_

  - [ ]* 4.3 Kimlik bilgisi round-trip özellik testi yaz
    - **Özellik 11: Kimlik Bilgisi Round-Trip**
    - **Doğrular: Gereksinim 6.1, 6.4**
    - `tests/property/test_storage_properties.py` içine `test_credential_round_trip` yaz

  - [ ]* 4.4 Eşik değeri kalıcılığı round-trip özellik testi yaz
    - **Özellik 5: Eşik Değeri Kalıcılığı Round-Trip**
    - **Doğrular: Gereksinim 4.2**
    - `test_threshold_persistence_round_trip` testini yaz; `None` dahil geçerli değerler için kaydet/oku döngüsünü doğrula

  - [ ]* 4.5 Geçersiz eşik değeri reddi özellik testi yaz
    - **Özellik 6: Geçersiz Eşik Değeri Reddi**
    - **Doğrular: Gereksinim 4.4**
    - `test_invalid_threshold_rejected` testini yaz; negatif sayı ve sayısal olmayan string için reddi doğrula

- [x] 5. AlarmManager bileşenini uygula
  - [x] 5.1 `src/alarm_manager.py` dosyasını oluştur ve `AlarmManager` sınıfını yaz
    - `QObject` miras alarak `alarm_triggered = pyqtSignal(str, int)` ve `alarm_silenced = pyqtSignal(str)` sinyallerini tanımla
    - `check_thresholds(totals: ResourceTotals)` metodunu uygula; her kaynak için bağımsız eşik kontrolü yap
    - `silence(resource)` ve `reset_silence(resource)` metodlarını uygula
    - Kaynak miktarı eşiğin altına düşünce susturma durumunu otomatik sıfırla
    - `QSoundEffect` ile alarm sesini çal
    - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 5.2 Devre dışı eşik alarm tetiklemez özellik testi yaz
    - **Özellik 7: Devre Dışı Eşik Alarm Tetiklemez**
    - **Doğrular: Gereksinim 4.5**
    - `tests/property/test_alarm_properties.py` içine `test_disabled_threshold_no_alarm` yaz

  - [ ]* 5.3 Alarm eşik kontrolü özellik testi yaz
    - **Özellik 8: Alarm Eşik Kontrolü**
    - **Doğrular: Gereksinim 5.1, 5.2**
    - `test_alarm_threshold_check` testini yaz; toplam >= eşik ise sinyal yayınlandığını, toplam < eşik ise yayınlanmadığını doğrula

  - [ ]* 5.4 Susturma sonrası alarm tekrarlanmaz özellik testi yaz
    - **Özellik 9: Susturma Sonrası Alarm Tekrarlanmaz**
    - **Doğrular: Gereksinim 5.5**
    - `test_silence_prevents_repeat_alarm` testini yaz

  - [ ]* 5.5 Susturma sıfırlama round-trip özellik testi yaz
    - **Özellik 10: Susturma Sıfırlama Round-Trip**
    - **Doğrular: Gereksinim 5.6**
    - `test_silence_reset_on_threshold_drop` testini yaz; tetikleme → susturma → düşme → tekrar eşiğe ulaşma döngüsünü doğrula

  - [ ]* 5.6 AlarmManager birim testlerini yaz
    - `tests/unit/test_alarm_manager.py` içine otomatik yeniden giriş denemesi ve başarısız giriş hata sinyali testlerini yaz
    - _Gereksinimler: 6.2, 6.3_

- [x] 6. ResourceTracker bileşenini uygula
  - [x] 6.1 `src/resource_tracker.py` dosyasını oluştur ve `ResourceTracker` sınıfını yaz
    - `QObject` miras alarak `data_updated`, `error_occurred`, `refresh_started`, `refresh_finished` sinyallerini tanımla
    - `QTimer` ile 60 saniyelik periyodik yenileme döngüsünü kur
    - `start()`, `stop()`, `refresh_now()` metodlarını uygula
    - `calculate_totals(villages) -> ResourceTotals` metodunu uygula
    - Scraping işlemini `QThread` içinde çalıştır; UI thread'ini bloke etme
    - `SessionExpiredError` yakalandığında otomatik yeniden giriş dene
    - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 6.2, 6.3_

  - [ ]* 6.2 Toplam kaynak hesaplama doğruluğu özellik testi yaz
    - **Özellik 4: Toplam Kaynak Hesaplama Doğruluğu**
    - **Doğrular: Gereksinim 3.1, 3.2, 3.3, 3.4**
    - `tests/property/test_calculation_properties.py` içine `test_calculate_totals_correctness` yaz
    - Hypothesis ile rastgele köy listesi üret; her kaynak toplamının aritmetik toplamla eşleştiğini doğrula

  - [ ]* 6.3 ResourceTracker birim testlerini yaz
    - `tests/unit/test_resource_tracker.py` içine `start()`/`stop()` döngüsü ve `last_updated` güncellenmesi testlerini yaz
    - _Gereksinimler: 2.2, 2.4_

- [x] 7. Kontrol noktası — Tüm testlerin geçtiğini doğrula
  - Tüm testlerin geçtiğini doğrula, sorular varsa kullanıcıya sor.

- [x] 8. Ana pencere (MainWindow) arayüzünü uygula
  - [x] 8.1 `src/main_window.py` dosyasını oluştur ve `MainWindow` sınıfını yaz
    - `QTableWidget` ile köy tablosunu oluştur; köy adı, odun, kil, demir, yiyecek sütunları
    - Tablonun altına toplam satırı ekle
    - Eşiğe ulaşan kaynakları renk değişikliğiyle vurgula
    - Durum çubuğuna son güncelleme zamanı ve bir sonraki yenileme zamanını göster
    - Başlat/Durdur düğmelerini ve manuel yenileme düğmesini ekle
    - `ResourceTracker` sinyallerine bağlan: `data_updated`, `error_occurred`, `refresh_finished`
    - _Gereksinimler: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 8.2 Eşik değeri giriş alanlarını ve doğrulama mantığını uygula
    - Her kaynak için `QSpinBox` veya `QLineEdit` ile eşik giriş alanı ekle
    - Devre dışı bırakma için `QCheckBox` ekle
    - Geçersiz giriş (negatif, sayısal olmayan) için hata mesajı göster
    - Değer değiştiğinde `SettingsStore.set_threshold()` çağır
    - _Gereksinimler: 4.1, 4.3, 4.4, 4.5_

  - [x] 8.3 Kimlik bilgisi giriş diyaloğunu (`LoginDialog`) uygula
    - `src/login_dialog.py` dosyasını oluştur
    - Kullanıcı adı ve şifre alanları, Giriş Yap düğmesi
    - `CredentialStore` ile kaydet/yükle entegrasyonu
    - _Gereksinimler: 6.1, 6.3_

- [x] 9. Alarm susturma ve görsel bildirim entegrasyonunu uygula
  - `AlarmManager.alarm_triggered` sinyalini `MainWindow`'a bağla
  - Alarm tetiklendiğinde ilgili kaynak satırını görsel olarak vurgula ve susturma düğmesi göster
  - Susturma düğmesine tıklandığında `AlarmManager.silence()` çağır
  - _Gereksinimler: 5.3, 5.5_

- [x] 10. Uygulama giriş noktasını ve bileşen bağlantısını tamamla
  - `src/main.py` dosyasını oluştur
  - `QApplication` başlat, `MainWindow`, `ResourceTracker`, `AlarmManager`, `CredentialStore`, `SettingsStore` örneklerini oluştur
  - Tüm sinyal/slot bağlantılarını kur
  - Uygulama başlangıcında kayıtlı kimlik bilgilerini yükle; yoksa `LoginDialog` göster
  - _Gereksinimler: 2.1, 6.1, 6.2, 6.3_

- [x] 11. Son kontrol noktası — Tüm testlerin geçtiğini doğrula
  - Tüm testlerin geçtiğini doğrula, sorular varsa kullanıcıya sor.

## Notlar

- `*` ile işaretli alt görevler isteğe bağlıdır; daha hızlı MVP için atlanabilir
- Her görev, izlenebilirlik için ilgili gereksinimlere referans verir
- Özellik testleri evrensel doğruluk özelliklerini, birim testleri ise belirli örnekleri ve kenar durumları doğrular
- Kontrol noktaları artımlı doğrulama sağlar
