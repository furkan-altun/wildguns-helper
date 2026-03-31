import { describe, it, expect, beforeEach, vi } from 'vitest';
import fc from 'fast-check';

// ─── localStorage mock ───────────────────────────────────────────────────────

let _store = {};
const localStorageMock = {
  getItem: (key) => _store[key] ?? null,
  setItem: (key, value) => { _store[key] = String(value); },
  removeItem: (key) => { delete _store[key]; },
  clear: () => { _store = {}; },
};

// Inject mock before importing module
global.localStorage = localStorageMock;

// Dynamic import helper — re-imports module with fresh state each time
async function freshI18n() {
  // Reset store
  _store = {};
  // Use a cache-busting query param trick via virtual module re-evaluation
  // Since vitest caches modules, we directly re-export from i18n.js and reset state via setLanguage
  const mod = await import('./i18n.js');
  // Reset to default state
  mod.setLanguage('tr');
  _store = {};
  return mod;
}

// ─── Property Tests ──────────────────────────────────────────────────────────

describe('I18n Property Tests', () => {
  let i18n;

  beforeEach(async () => {
    _store = {};
    i18n = await import('./i18n.js');
    // Reset to tr
    i18n.setLanguage('tr');
    _store = {};
  });

  // Feature: wildguns-i18n-support, Property 1: setLanguage state ve storage round-trip
  // Validates: Requirements 1.2, 3.1
  it('Property 1: setLanguage state ve storage round-trip', () => {
    const validLangs = fc.constantFrom('tr', 'en');
    fc.assert(
      fc.property(validLangs, (lang) => {
        _store = {};
        i18n.setLanguage(lang);
        expect(i18n.getLanguage()).toBe(lang);
        expect(_store['wg_language']).toBe(lang);
      }),
      { numRuns: 100 }
    );
  });

  // Feature: wildguns-i18n-support, Property 2: loadLanguage round-trip
  // Validates: Requirements 3.2
  it('Property 2: loadLanguage round-trip', () => {
    const validLangs = fc.constantFrom('tr', 'en');
    fc.assert(
      fc.property(validLangs, (lang) => {
        _store = {};
        _store['wg_language'] = lang;
        i18n.loadLanguage();
        expect(i18n.getLanguage()).toBe(lang);
      }),
      { numRuns: 100 }
    );
  });

  // Feature: wildguns-i18n-support, Property 3: Her iki dilde tüm key'ler tanımlı
  // Validates: Requirements 2.1, 4.2, 5.2
  it('Property 3: Her iki dilde tüm key\'ler tanımlı', () => {
    const allKeys = Object.keys(i18n.TRANSLATIONS.tr);
    fc.assert(
      fc.property(fc.constantFrom(...allKeys), (key) => {
        expect(typeof i18n.TRANSLATIONS.tr[key]).toBe('string');
        expect(typeof i18n.TRANSLATIONS.en[key]).toBe('string');
      }),
      { numRuns: 100 }
    );
  });

  // Feature: wildguns-i18n-support, Property 4: t(key) aktif dildeki değeri döndürür
  // Validates: Requirements 2.2, 4.1, 5.1
  it('Property 4: t(key) aktif dildeki değeri döndürür', () => {
    const validLangs = fc.constantFrom('tr', 'en');
    const allKeys = Object.keys(i18n.TRANSLATIONS.tr);
    fc.assert(
      fc.property(validLangs, fc.constantFrom(...allKeys), (lang, key) => {
        _store = {};
        i18n.setLanguage(lang);
        expect(i18n.t(key)).toBe(i18n.TRANSLATIONS[lang][key]);
      }),
      { numRuns: 100 }
    );
  });

  // Feature: wildguns-i18n-support, Property 5: Fallback zinciri
  // Validates: Requirements 2.3, 2.4
  it('Property 5: Fallback zinciri — eksik key key\'in kendisini döndürür', () => {
    fc.assert(
      fc.property(fc.string({ minLength: 1 }).filter(s => !(s in i18n.TRANSLATIONS.tr) && !(s in i18n.TRANSLATIONS.en)), (unknownKey) => {
        i18n.setLanguage('tr');
        expect(i18n.t(unknownKey)).toBe(unknownKey);
        i18n.setLanguage('en');
        expect(i18n.t(unknownKey)).toBe(unknownKey);
      }),
      { numRuns: 100 }
    );
  });

  // Feature: wildguns-i18n-support, Property 6: Varsayılan dil tr
  // Validates: Requirements 3.3
  it('Property 6: Varsayılan dil tr — localStorage boşken loadLanguage tr döndürür', () => {
    fc.assert(
      fc.property(fc.constant(null), () => {
        _store = {};
        i18n.loadLanguage();
        expect(i18n.getLanguage()).toBe('tr');
      }),
      { numRuns: 100 }
    );
  });
});

// ─── Unit Tests ──────────────────────────────────────────────────────────────

describe('I18n Unit Tests', () => {
  let i18n;

  beforeEach(async () => {
    _store = {};
    i18n = await import('./i18n.js');
    i18n.setLanguage('tr');
    _store = {};
  });

  // Requirements: 4.3
  it('en panel başlığı doğru', () => {
    i18n.setLanguage('en');
    expect(i18n.t('panel_title')).toBe('🤠 Wildguns Resource Tracker');
  });

  // Requirements: 4.4
  it('en tablo başlıkları doğru', () => {
    i18n.setLanguage('en');
    expect(i18n.t('col_village')).toBe('Village Name');
    expect(i18n.t('col_wood')).toBe('Wood');
    expect(i18n.t('col_clay')).toBe('Clay');
    expect(i18n.t('col_iron')).toBe('Iron');
    expect(i18n.t('col_food')).toBe('Food');
    expect(i18n.t('col_total')).toBe('Total');
  });

  // Requirements: 4.5
  it('en buton etiketleri doğru', () => {
    i18n.setLanguage('en');
    expect(i18n.t('btn_start')).toBe('▶ Auto Start');
    expect(i18n.t('btn_stop')).toBe('■ Stop');
    expect(i18n.t('btn_refresh')).toBe('🔍 Refresh Now');
  });

  // Requirements: 4.6
  it('en alarm modu etiketleri doğru', () => {
    i18n.setLanguage('en');
    expect(i18n.t('mode_grand_total')).toBe('Grand Total');
    expect(i18n.t('mode_per_resource')).toBe('Per Resource');
  });

  // Requirements: 5.3
  it('tr panel başlığı doğru', () => {
    i18n.setLanguage('tr');
    expect(i18n.t('panel_title')).toBe('🤠 Wildguns Kaynak Takip');
  });

  // Requirements: 5.4
  it('tr tablo başlıkları doğru', () => {
    i18n.setLanguage('tr');
    expect(i18n.t('col_village')).toBe('Köy Adı');
    expect(i18n.t('col_wood')).toBe('Odun');
    expect(i18n.t('col_clay')).toBe('Kil');
    expect(i18n.t('col_iron')).toBe('Demir');
    expect(i18n.t('col_food')).toBe('Yiyecek');
    expect(i18n.t('col_total')).toBe('Toplam');
  });

  // Requirements: 5.5
  it('tr buton etiketleri doğru', () => {
    i18n.setLanguage('tr');
    expect(i18n.t('btn_start')).toBe('▶ Otomatik Başlat');
    expect(i18n.t('btn_stop')).toBe('■ Durdur');
    expect(i18n.t('btn_refresh')).toBe('🔍 Şimdi Yenile');
  });

  // Requirements: 5.6
  it('tr alarm modu etiketleri doğru', () => {
    i18n.setLanguage('tr');
    expect(i18n.t('mode_grand_total')).toBe('Genel Toplam');
    expect(i18n.t('mode_per_resource')).toBe('Kaynak Bazlı');
  });

  // Requirements: 3.3
  it('localStorage boşken varsayılan tr', () => {
    _store = {};
    i18n.loadLanguage();
    expect(i18n.getLanguage()).toBe('tr');
  });

  // Error Handling
  it('localStorage hata durumunda varsayılan tr', () => {
    const originalGetItem = localStorageMock.getItem;
    localStorageMock.getItem = () => { throw new Error('storage error'); };
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    i18n.loadLanguage();
    expect(i18n.getLanguage()).toBe('tr');
    expect(warnSpy).toHaveBeenCalled();
    localStorageMock.getItem = originalGetItem;
    warnSpy.mockRestore();
  });

  it('setLanguage bilinmeyen dil kodunda mevcut dili korur', () => {
    i18n.setLanguage('tr');
    i18n.setLanguage('de');
    expect(i18n.getLanguage()).toBe('tr');
    i18n.setLanguage('en');
    i18n.setLanguage('fr');
    expect(i18n.getLanguage()).toBe('en');
  });

  it('t(key) bilinmeyen key için key\'in kendisini döndürür', () => {
    i18n.setLanguage('tr');
    expect(i18n.t('nonexistent_key_xyz')).toBe('nonexistent_key_xyz');
  });
});
