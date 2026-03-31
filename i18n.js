// i18n module — extracted for testability

let _lang = 'tr';

const TRANSLATIONS = {
  tr: {
    panel_title:        '🤠 Wildguns Kaynak Takip',
    tab_resources:      '📦 Hammadde Takibi',
    tab_alliance:       '🗺️ İttifak Lokasyon',
    col_village:        'Köy Adı',
    col_wood:           'Odun',
    col_clay:           'Kil',
    col_iron:           'Demir',
    col_food:           'Yiyecek',
    col_total:          'Toplam',
    btn_start:          '▶ Otomatik Başlat',
    btn_stop:           '■ Durdur',
    btn_refresh:        '🔍 Şimdi Yenile',
    btn_refreshing:     'Yenileniyor...',
    label_interval:     'Aralık',
    label_interval_unit:'sn',
    label_last_update:  'Son güncelleme',
    label_target:       'Hedef',
    mode_grand_total:   'Genel Toplam',
    mode_per_resource:  'Kaynak Bazlı',
    label_wood:         'Odun',
    label_clay:         'Kil',
    label_iron:         'Demir',
    label_food:         'Yiyecek',
    no_data:            'Henüz veri yok — Yenile butonuna basın',
    total_row:          'TOPLAM',
    target_none:        'Hedef: —',
    target_progress:    'Hedef: %{pct} ({current} / {target})',
    alarm_reached:      '🎯 Hedefe ulaşıldı! Otomatik yenileme durduruldu.',
    alarm_notification: '🎯 Hedefe ulaşıldı!',
    popup_ok:           'Tamam',
    coming_soon:        'Yakında eklenecektir...',
    alliance_title:     'İttifak Lokasyon',
    err_table_not_found:'Köy tablosu bulunamadı',
    err_session_expired:'Oturum süresi dolmuş — lütfen giriş yapın',
    err_parse_error:    'Tabloda geçerli köy satırı bulunamadı',
    err_network_error:  'Fetch hatası',
  },
  en: {
    panel_title:        '🤠 Wildguns Resource Tracker',
    tab_resources:      '📦 Resource Tracking',
    tab_alliance:       '🗺️ Alliance Location',
    col_village:        'Village Name',
    col_wood:           'Wood',
    col_clay:           'Clay',
    col_iron:           'Iron',
    col_food:           'Food',
    col_total:          'Total',
    btn_start:          '▶ Auto Start',
    btn_stop:           '■ Stop',
    btn_refresh:        '🔍 Refresh Now',
    btn_refreshing:     'Refreshing...',
    label_interval:     'Interval',
    label_interval_unit:'sec',
    label_last_update:  'Last updated',
    label_target:       'Target',
    mode_grand_total:   'Grand Total',
    mode_per_resource:  'Per Resource',
    label_wood:         'Wood',
    label_clay:         'Clay',
    label_iron:         'Iron',
    label_food:         'Food',
    no_data:            'No data yet — press Refresh',
    total_row:          'TOTAL',
    target_none:        'Target: —',
    target_progress:    'Target: {pct}% ({current} / {target})',
    alarm_reached:      '🎯 Target reached! Auto refresh stopped.',
    alarm_notification: '🎯 Target reached!',
    popup_ok:           'OK',
    coming_soon:        'Coming soon...',
    alliance_title:     'Alliance Location',
    err_table_not_found:'Village table not found',
    err_session_expired:'Session expired — please log in',
    err_parse_error:    'No valid village rows found in table',
    err_network_error:  'Fetch error',
  },
};

function t(key) {
  if (TRANSLATIONS[_lang] && TRANSLATIONS[_lang][key] !== undefined) {
    return TRANSLATIONS[_lang][key];
  }
  if (TRANSLATIONS['en'] && TRANSLATIONS['en'][key] !== undefined) {
    return TRANSLATIONS['en'][key];
  }
  return key;
}

function setLanguage(lang) {
  if (lang !== 'tr' && lang !== 'en') return;
  _lang = lang;
  try {
    localStorage.setItem('wg_language', lang);
  } catch (e) {
    console.warn('setLanguage storage hatası:', e);
  }
}

function loadLanguage() {
  try {
    const stored = localStorage.getItem('wg_language');
    if (stored === 'tr' || stored === 'en') {
      _lang = stored;
    } else {
      _lang = 'tr';
    }
  } catch (e) {
    console.warn('loadLanguage storage hatası:', e);
    _lang = 'tr';
  }
}

function getLanguage() {
  return _lang;
}

export { _lang, TRANSLATIONS, t, setLanguage, loadLanguage, getLanguage };
