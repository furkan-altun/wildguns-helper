class TrackerError(Exception):
    """Uygulama hata hiyerarşisinin temel sınıfı."""
    ...


class NetworkError(TrackerError):
    """Sayfa yüklenemediğinde veya ağ hatası oluştuğunda fırlatılır."""
    ...


class ParseError(TrackerError):
    """HTML ayrıştırma başarısız olduğunda veya beklenen tablo bulunamadığında fırlatılır."""
    ...


class AuthenticationError(TrackerError):
    """Kimlik doğrulama başarısız olduğunda fırlatılır."""
    ...


class SessionExpiredError(TrackerError):
    """Oturum süresi dolduğunda veya geçersiz hale geldiğinde fırlatılır."""
    ...
