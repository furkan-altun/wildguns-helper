# Gereksinimler Belgesi

## Giriş

Wildguns Kaynak Takip ve Alarm Uygulaması, `tr.wildguns.gameforge.com` adresindeki tarayıcı tabanlı strateji oyununun "Köy Genel Durum" ekranını periyodik olarak okuyarak oyuncunun tüm köylerindeki hammadde (odun, kil, demir, yiyecek) toplamlarını hesaplar. Belirlenen eşik değerlerine ulaşıldığında kullanıcıya sesli alarm ile bildirim verir. Uygulama Windows ve macOS işletim sistemlerinde çalışır.

## Sözlük

- **Uygulama**: Wildguns Kaynak Takip ve Alarm masaüstü uygulaması
- **Scraper**: Oyun web sayfasından veri çeken bileşen
- **Alarm_Yoneticisi**: Eşik değerlerini kontrol eden ve sesli alarm tetikleyen bileşen
- **Kaynak**: Oyundaki hammaddelerden biri — odun, kil, demir veya yiyecek
- **Koy**: Oyuncunun sahip olduğu tek bir köy birimi
- **Esik_Degeri**: Kullanıcının her kaynak için belirlediği, alarmı tetikleyen minimum miktar
- **Toplam_Kaynak**: Tüm köylerdeki aynı türdeki kaynakların toplamı
- **Oturum**: Kullanıcının oyun sitesine giriş yapmış aktif tarayıcı oturumu

---

## Gereksinimler

### Gereksinim 1: Web Scraping ile Veri Okuma

**Kullanıcı Hikayesi:** Bir oyuncu olarak, oyun sayfasını manuel olarak açmak zorunda kalmadan köylerimin hammadde miktarlarının otomatik okunmasını istiyorum; böylece oyunu sürekli takip etmek zorunda kalmam.

#### Kabul Kriterleri

1. THE Scraper SHALL `tr.wildguns.gameforge.com/user.php?action=overview&view=over` adresindeki "Köy Genel Durum" tablosunu okuyarak her köy için odun, kil, demir ve yiyecek değerlerini ayrıştırır.
2. WHEN sayfa başarıyla yüklendiğinde, THE Scraper SHALL tablodaki tüm köy satırlarını tespit eder ve her satırdan köy adı, odun, kil, demir ve yiyecek sütun değerlerini sayısal olarak çıkarır.
3. WHEN tabloda birden fazla köy satırı bulunduğunda, THE Scraper SHALL her köyün verilerini ayrı ayrı kaydeder.
4. IF sayfa yüklenemezse veya tablo bulunamazsa, THEN THE Scraper SHALL hata mesajını kullanıcı arayüzünde gösterir ve bir sonraki yenileme döngüsünde tekrar dener.
5. IF kullanıcı oyun sitesine giriş yapmamışsa, THEN THE Scraper SHALL kullanıcıyı giriş yapması gerektiği konusunda uyarır.

---

### Gereksinim 2: Otomatik Periyodik Yenileme

**Kullanıcı Hikayesi:** Bir oyuncu olarak, uygulamanın her dakika otomatik olarak veriyi güncellemesini istiyorum; böylece kaynak miktarlarını gerçek zamanlıya yakın takip edebileyim.

#### Kabul Kriterleri

1. THE Uygulama SHALL başlatıldıktan sonra her 60 saniyede bir Scraper'ı tetikleyerek veriyi yeniler.
2. WHEN yenileme tamamlandığında, THE Uygulama SHALL son güncelleme zamanını kullanıcı arayüzünde gösterir.
3. WHILE yenileme devam ederken, THE Uygulama SHALL kullanıcı arayüzünü kilitlemez ve kullanıcının eşik değerlerini düzenlemesine izin verir.
4. THE Uygulama SHALL kullanıcının yenileme döngüsünü manuel olarak başlatmasına ve durdurmasına olanak tanır.

---

### Gereksinim 3: Toplam Kaynak Hesaplama

**Kullanıcı Hikayesi:** Bir oyuncu olarak, tüm köylerimdeki her kaynak türünün toplamını görmek istiyorum; böylece genel kaynak durumumu tek bakışta anlayabilirim.

#### Kabul Kriterleri

1. WHEN Scraper veri çekmeyi tamamladığında, THE Uygulama SHALL tüm köylerdeki odun değerlerini toplayarak toplam odun miktarını hesaplar.
2. WHEN Scraper veri çekmeyi tamamladığında, THE Uygulama SHALL tüm köylerdeki kil değerlerini toplayarak toplam kil miktarını hesaplar.
3. WHEN Scraper veri çekmeyi tamamladığında, THE Uygulama SHALL tüm köylerdeki demir değerlerini toplayarak toplam demir miktarını hesaplar.
4. WHEN Scraper veri çekmeyi tamamladığında, THE Uygulama SHALL tüm köylerdeki yiyecek değerlerini toplayarak toplam yiyecek miktarını hesaplar.
5. THE Uygulama SHALL her kaynak türünün toplamını ve köy bazlı dökümünü kullanıcı arayüzünde gösterir.

---

### Gereksinim 4: Eşik Değeri Yapılandırması

**Kullanıcı Hikayesi:** Bir oyuncu olarak, her kaynak türü için ayrı ayrı alarm eşik değerleri belirlemek istiyorum; böylece hangi kaynağın ne zaman yeterli miktara ulaştığını özelleştirebilirim.

#### Kabul Kriterleri

1. THE Uygulama SHALL kullanıcının odun, kil, demir ve yiyecek için ayrı ayrı toplam eşik değerleri girmesine olanak tanır.
2. THE Uygulama SHALL girilen eşik değerlerini uygulama kapatılıp açılsa dahi kalıcı olarak saklar.
3. WHEN kullanıcı eşik değerini değiştirdiğinde, THE Uygulama SHALL yeni değeri anında etkinleştirir ve bir sonraki kontrol döngüsünde kullanır.
4. IF kullanıcı geçersiz bir değer girerse (negatif sayı veya sayısal olmayan değer), THEN THE Uygulama SHALL girişi reddeder ve kullanıcıya açıklayıcı hata mesajı gösterir.
5. THE Uygulama SHALL her kaynak için eşik değerini devre dışı bırakma seçeneği sunar; devre dışı bırakılan eşikler alarm tetiklemez.

---

### Gereksinim 5: Sesli Alarm Bildirimi

**Kullanıcı Hikayesi:** Bir oyuncu olarak, kaynak miktarı belirlediğim eşiğe ulaştığında sesli uyarı almak istiyorum; böylece ekranı sürekli izlemek zorunda kalmam.

#### Kabul Kriterleri

1. WHEN herhangi bir kaynağın toplam miktarı ilgili eşik değerine ulaştığında veya aştığında, THE Alarm_Yoneticisi SHALL sesli alarm çalar.
2. THE Alarm_Yoneticisi SHALL her kaynak türü için bağımsız alarm tetikler; bir kaynağın alarmı diğer kaynakların alarmını etkilemez.
3. WHEN alarm tetiklendiğinde, THE Uygulama SHALL hangi kaynağın eşiğe ulaştığını kullanıcı arayüzünde görsel olarak da belirtir.
4. THE Uygulama SHALL alarm sesini kullanıcının işletim sistemi ses seviyesine göre çalar.
5. IF alarm çalarken kullanıcı alarmı susturmak isterse, THEN THE Uygulama SHALL alarmı durdurur ve bir sonraki eşik aşımına kadar aynı kaynak için tekrar alarm çalmaz.
6. WHEN kaynak miktarı eşik değerinin altına düştükten sonra tekrar eşiğe ulaştığında, THE Alarm_Yoneticisi SHALL alarmı yeniden tetikler.

---

### Gereksinim 6: Kimlik Doğrulama ve Oturum Yönetimi

**Kullanıcı Hikayesi:** Bir oyuncu olarak, oyun sitesine giriş bilgilerimi uygulamaya girebilmek istiyorum; böylece uygulama sayfayı otomatik olarak okuyabilsin.

#### Kabul Kriterleri

1. THE Uygulama SHALL kullanıcının oyun sitesi kullanıcı adı ve şifresini güvenli biçimde saklar.
2. WHEN oturum süresi dolduğunda veya geçersiz hale geldiğinde, THE Scraper SHALL otomatik olarak yeniden giriş yapmayı dener.
3. IF otomatik yeniden giriş başarısız olursa, THEN THE Uygulama SHALL kullanıcıyı bilgilendirir ve manuel giriş yapmasını ister.
4. THE Uygulama SHALL kullanıcı şifresini işletim sisteminin güvenli anahtar deposunda (Keychain veya Windows Credential Manager) saklar.

---

### Gereksinim 7: Kullanıcı Arayüzü

**Kullanıcı Hikayesi:** Bir oyuncu olarak, kaynak miktarlarını ve alarm durumlarını net biçimde görebileceğim bir arayüz istiyorum; böylece bilgilere hızlıca ulaşabilirim.

#### Kabul Kriterleri

1. THE Uygulama SHALL her köyün adını ve o köydeki odun, kil, demir, yiyecek miktarlarını tablo biçiminde gösterir.
2. THE Uygulama SHALL tüm köylerin toplam odun, kil, demir ve yiyecek miktarlarını tablonun altında özet satırı olarak gösterir.
3. THE Uygulama SHALL eşik değerine ulaşan veya aşan kaynakları görsel olarak vurgular (örneğin renk değişikliği).
4. THE Uygulama SHALL Windows ve macOS işletim sistemlerinde yerel masaüstü uygulaması olarak çalışır.
5. THE Uygulama SHALL farklı ekran çözünürlüklerinde düzgün biçimde görüntülenir; arayüz bileşenleri çözünürlüğe göre ölçeklenir.
6. THE Uygulama SHALL son başarılı veri çekme zamanını ve bir sonraki yenileme zamanını gösterir.
