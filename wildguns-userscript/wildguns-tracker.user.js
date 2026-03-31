// ==UserScript==
// @name         Wildguns Kaynak Takip
// @namespace    https://github.com/furkan-altun/wildguns-tracker
// @version      2.1.0
// @description  Wildguns köy kaynaklarını otomatik takip eder
// @match        https://s1-tr.wildguns.gameforge.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function() {
  'use strict';

  // ─── i18n ───────────────────────────────────────────────────────────────────

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

  // ─── utils.js ───────────────────────────────────────────────────────────────

  function validateInterval(n) {
    if (n < 10) return 10;
    if (n > 3600) return 3600;
    return n;
  }

  function formatNumber(n) {
    return n.toLocaleString('tr-TR');
  }

  function formatTime(date) {
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    const ss = String(date.getSeconds()).padStart(2, '0');
    return `${hh}:${mm}:${ss}`;
  }

  function calculateProgress(current, target) {
    if (target <= 0) return 0;
    return Math.min(100, Math.floor((current / target) * 100));
  }

  // ─── parser.js ──────────────────────────────────────────────────────────────

  function parseResource(text) {
    const cleaned = text.replace(/[.,\s]/g, '');
    const n = parseInt(cleaned, 10);
    return isNaN(n) ? NaN : n;
  }

  function parseVillageTable(root) {
    if (root === undefined) {
      root = typeof document !== 'undefined' ? document : null;
    }
    try {
      if (!root) {
        return { success: false, error: 'table_not_found', message: 'Köy tablosu bulunamadı' };
      }
      const passInput = root.querySelector('input[name="pass"]');
      const loginForm = root.querySelector('form[action*="action=login"]');
      if (passInput || loginForm) {
        return { success: false, error: 'session_expired', message: 'Oturum süresi dolmuş — lütfen giriş yapın' };
      }
      const tables = root.querySelectorAll('table');
      let villageTable = null;
      for (const table of tables) {
        if (table.querySelector('a[href*="switchvillage="]')) {
          villageTable = table;
          break;
        }
      }
      if (!villageTable) {
        return { success: false, error: 'table_not_found', message: 'Köy tablosu bulunamadı' };
      }
      const rows = villageTable.querySelectorAll('tr');
      const villages = [];
      for (const row of rows) {
        if (row.querySelector('th')) continue;
        const cells = row.querySelectorAll('td');
        if (cells.length < 6) continue;
        const name = cells[0].textContent.trim();
        if (!name) continue;
        const wood = parseResource(cells[1].textContent.trim());
        const clay = parseResource(cells[2].textContent.trim());
        const iron = parseResource(cells[3].textContent.trim());
        const food = parseResource(cells[5].textContent.trim());
        if (isNaN(wood) || isNaN(clay) || isNaN(iron) || isNaN(food)) continue;
        const rowTotal = wood + clay + iron + food;
        villages.push({ name, wood, clay, iron, food, rowTotal });
      }
      if (villages.length === 0) {
        return { success: false, error: 'parse_error', message: 'Tabloda geçerli köy satırı bulunamadı' };
      }
      return { success: true, villages };
    } catch (e) {
      return { success: false, error: 'parse_error', message: 'Tabloda geçerli köy satırı bulunamadı' };
    }
  }

  // ─── tracker.js ─────────────────────────────────────────────────────────────

  let _intervalId = null;

  function calculateTotals(villages) {
    const totals = { wood: 0, clay: 0, iron: 0, food: 0, grandTotal: 0 };
    for (const v of villages) {
      totals.wood += v.wood;
      totals.clay += v.clay;
      totals.iron += v.iron;
      totals.food += v.food;
    }
    totals.grandTotal = totals.wood + totals.clay + totals.iron + totals.food;
    return totals;
  }

  function _runCycle(onData, onError) {
    const url = 'https://s1-tr.wildguns.gameforge.com/user.php?action=overview&view=over';
    fetch(url, { credentials: 'include' })
      .then(r => r.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const result = parseVillageTable(doc);
        if (result.success) {
          const totals = calculateTotals(result.villages);
          onData(result.villages, totals);
        } else {
          onError(result);
        }
      })
      .catch(e => onError({ success: false, error: 'network_error', message: 'Fetch hatası: ' + e.message }));
  }

  function startTracker(intervalSecs, onData, onError) {
    const validSecs = validateInterval(intervalSecs);
    _runCycle(onData, onError);
    _intervalId = setInterval(() => {
      _runCycle(onData, onError);
    }, validSecs * 1000);
  }

  function stopTracker() {
    if (_intervalId !== null) {
      clearInterval(_intervalId);
      _intervalId = null;
    }
  }

  // ─── alarm.js ───────────────────────────────────────────────────────────────

  function checkAlarm(totals, thresholds, alarmMode, alarmFired) {
    if (alarmFired) return { triggered: false, alarmFired: true };
    if (alarmMode === 'grand_total') {
      const target = thresholds.grandTotal;
      if (!target || target <= 0) return { triggered: false, alarmFired: false };
      if (totals.grandTotal >= target) return { triggered: true, alarmFired: true };
      return { triggered: false, alarmFired: false };
    }
    if (alarmMode === 'per_resource') {
      const target = (thresholds.wood||0) + (thresholds.clay||0) + (thresholds.iron||0) + (thresholds.food||0);
      if (target <= 0) return { triggered: false, alarmFired: false };
      if (totals.grandTotal >= target) return { triggered: true, alarmFired: true };
      return { triggered: false, alarmFired: false };
    }
    return { triggered: false, alarmFired: false };
  }

  // ─── storage ────────────────────────────────────────────────────────────────

  const DEFAULTS = {
    intervalSecs: 60,
    alarmMode: 'grand_total',
    thresholds: { wood: 0, clay: 0, iron: 0, food: 0, grandTotal: 0 },
  };

  function saveSettings(settings) {
    try {
      localStorage.setItem('wg_intervalSecs', settings.intervalSecs);
      localStorage.setItem('wg_alarmMode', settings.alarmMode);
      localStorage.setItem('wg_thresholds', JSON.stringify(settings.thresholds));
    } catch(e) { console.warn('saveSettings hata:', e); }
  }

  function loadSettings() {
    try {
      const intervalSecs = parseInt(localStorage.getItem('wg_intervalSecs'), 10) || DEFAULTS.intervalSecs;
      const alarmMode = localStorage.getItem('wg_alarmMode') || DEFAULTS.alarmMode;
      const thresholdsRaw = localStorage.getItem('wg_thresholds');
      let thresholds = { ...DEFAULTS.thresholds };
      if (thresholdsRaw) {
        try { thresholds = { ...DEFAULTS.thresholds, ...JSON.parse(thresholdsRaw) }; } catch(_) {}
      }
      return { intervalSecs, alarmMode, thresholds };
    } catch(e) {
      return { intervalSecs: DEFAULTS.intervalSecs, alarmMode: DEFAULTS.alarmMode, thresholds: { ...DEFAULTS.thresholds } };
    }
  }

  function saveVillageData(villages, lastUpdated) {
    try {
      localStorage.setItem('wg_villages', JSON.stringify(villages));
      localStorage.setItem('wg_lastUpdated', lastUpdated);
    } catch(e) {}
  }

  function loadVillageData() {
    try {
      const villagesRaw = localStorage.getItem('wg_villages');
      const lastUpdated = localStorage.getItem('wg_lastUpdated');
      let villages = [];
      if (villagesRaw) { try { villages = JSON.parse(villagesRaw); } catch(_) {} }
      return { villages, lastUpdated: lastUpdated || null };
    } catch(e) {
      return { villages: [], lastUpdated: null };
    }
  }

  // ─── alarm.js ───────────────────────────────────────────────────────────────

  const DEFAULTS = {(totals, thresholds, alarmMode, alarmFired) {
    if (alarmFired) return { triggered: false, alarmFired: true };
    if (alarmMode === 'grand_total') {
      const target = thresholds.grandTotal;
      if (!target || target <= 0) return { triggered: false, alarmFired: false };
      if (totals.grandTotal >= target) return { triggered: true, alarmFired: true };
      return { triggered: false, alarmFired: false };
    }
    if (alarmMode === 'per_resource') {
      // 4 kutudaki değerlerin toplamı hedef, grandTotal ile karşılaştır
      const target = (thresholds.wood||0) + (thresholds.clay||0) + (thresholds.iron||0) + (thresholds.food||0);
      if (target <= 0) return { triggered: false, alarmFired: false };
      if (totals.grandTotal >= target) return { triggered: true, alarmFired: true };
      return { triggered: false, alarmFired: false };
    }
    return { triggered: false, alarmFired: false };
  }

  function playAlarmSound() {
    try {
      const audio = new Audio('https://s1-tr.wildguns.gameforge.com/alarm.wav');
      audio.play();
    } catch (e) {
      console.warn('Alarm sesi çalınamadı:', e);
    }
  }

  function sendNotification(message) {
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      new Notification('Wildguns Kaynak Takip', { body: message });
    }
  }

  // ─── ui ─────────────────────────────────────────────────────────────────────

  let _callbacks = {};

  function createPanel(callbacks) {
    _callbacks = callbacks || {};
    const existing = document.getElementById('wg-tracker-panel');
    if (existing) existing.remove();
    const panel = document.createElement('div');
    panel.id = 'wg-tracker-panel';
    panel.style.cssText = [
      'position:fixed','top:20px','right:20px','z-index:999999',
      'width:min(380px,95vw)','background:#1e1e2e','color:#cdd6f4',
      'border:1px solid #45475a','border-radius:8px','font-family:sans-serif',
      'font-size:13px','box-shadow:0 4px 20px rgba(0,0,0,0.5)','user-select:none',
    ].join(';');
    panel.innerHTML = `
      <div id="wg-header" style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#313244;border-radius:8px 8px 0 0;cursor:move;border-bottom:1px solid #45475a;">
        <span id="wg-panel-title" style="font-weight:bold;font-size:14px;">🤠 Wildguns Kaynak Takip</span>
        <div style="display:flex;gap:4px;align-items:center;">
          <button id="wg-lang-tr" style="background:#89b4fa;color:#1e1e2e;border:none;border-radius:4px;padding:2px 7px;cursor:pointer;font-size:12px;font-weight:bold;height:24px;">[TR]</button>
          <button id="wg-lang-en" style="background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:2px 7px;cursor:pointer;font-size:12px;font-weight:bold;height:24px;">[EN]</button>
          <button id="wg-minimize" style="background:none;border:none;color:#cdd6f4;cursor:pointer;font-size:18px;width:32px;height:32px;line-height:1;">−</button>
          <button id="wg-close" style="background:none;border:none;color:#f38ba8;cursor:pointer;font-size:18px;width:32px;height:32px;line-height:1;">✕</button>
        </div>
      </div>
      <div id="wg-body">
        <div id="wg-tabs" style="display:flex;border-bottom:1px solid #45475a;background:#181825;">
          <button id="wg-tab-resources" style="flex:1;padding:8px 4px;background:#1e1e2e;color:#89b4fa;border:none;border-bottom:2px solid #89b4fa;cursor:pointer;font-size:12px;font-weight:bold;">📦 Hammadde Takibi</button>
          <button id="wg-tab-alliance" style="flex:1;padding:8px 4px;background:#181825;color:#6c7086;border:none;border-bottom:2px solid transparent;cursor:pointer;font-size:12px;font-weight:bold;">🗺️ İttifak Lokasyon</button>
        </div>

        <div id="wg-content-resources">
          <div style="overflow-y:auto;max-height:200px;padding:8px;">
            <table id="wg-resource-table" style="width:100%;border-collapse:collapse;font-size:12px;">
              <thead><tr style="color:#89b4fa;border-bottom:1px solid #45475a;">
                <th style="text-align:left;padding:4px 6px;">Köy Adı</th>
                <th style="text-align:right;padding:4px 6px;">Odun</th>
                <th style="text-align:right;padding:4px 6px;">Kil</th>
                <th style="text-align:right;padding:4px 6px;">Demir</th>
                <th style="text-align:right;padding:4px 6px;">Yiyecek</th>
                <th style="text-align:right;padding:4px 6px;">Toplam</th>
              </tr></thead>
              <tbody id="wg-table-body">
                <tr><td colspan="6" style="text-align:center;padding:8px;color:#6c7086;">Henüz veri yok — Yenile butonuna basın</td></tr>
              </tbody>
            </table>
          </div>
          <div style="padding:8px 12px;border-top:1px solid #45475a;">
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
              <button id="wg-start" style="background:#89b4fa;color:#1e1e2e;border:none;border-radius:4px;padding:8px 12px;cursor:pointer;font-weight:bold;flex:1;">▶ Otomatik Başlat</button>
              <button id="wg-stop" style="background:#f38ba8;color:#1e1e2e;border:none;border-radius:4px;padding:8px 12px;cursor:pointer;font-weight:bold;flex:1;opacity:0.4;" disabled>■ Durdur</button>
              <button id="wg-refresh" style="background:#a6e3a1;color:#1e1e2e;border:none;border-radius:4px;padding:8px 12px;cursor:pointer;font-weight:bold;flex:1;">🔍 Şimdi Yenile</button>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <label style="color:#a6adc8;">Aralık:</label>
              <input id="wg-interval" type="number" min="10" max="3600" value="60" style="width:70px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 8px;">
              <span style="color:#a6adc8;">sn</span>
            </div>
            <div id="wg-last-update" style="color:#6c7086;font-size:12px;">Son güncelleme: —</div>
          </div>
          <div style="padding:8px 12px;border-top:1px solid #45475a;">
            <div style="display:flex;gap:12px;margin-bottom:8px;">
              <label style="cursor:pointer;display:flex;align-items:center;gap:4px;"><input type="radio" name="wg-alarm-mode" id="wg-mode-grand" value="grand_total" checked style="accent-color:#89b4fa;"> Genel Toplam</label>
              <label style="cursor:pointer;display:flex;align-items:center;gap:4px;"><input type="radio" name="wg-alarm-mode" id="wg-mode-per" value="per_resource" style="accent-color:#89b4fa;"> Kaynak Bazlı</label>
            </div>
            <div id="wg-grand-input-row" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <label style="color:#a6adc8;">Hedef:</label>
              <input id="wg-grand-target" type="number" min="0" value="0" style="width:120px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 8px;">
            </div>
            <div id="wg-per-resource-inputs" style="display:none;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:4px;"><label style="color:#a6adc8;min-width:55px;">Odun:</label><input id="wg-threshold-wood" type="number" min="0" value="0" data-resource="wood" style="width:90px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 6px;"></div>
                <div style="display:flex;align-items:center;gap:4px;"><label style="color:#a6adc8;min-width:55px;">Kil:</label><input id="wg-threshold-clay" type="number" min="0" value="0" data-resource="clay" style="width:90px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 6px;"></div>
                <div style="display:flex;align-items:center;gap:4px;"><label style="color:#a6adc8;min-width:55px;">Demir:</label><input id="wg-threshold-iron" type="number" min="0" value="0" data-resource="iron" style="width:90px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 6px;"></div>
                <div style="display:flex;align-items:center;gap:4px;"><label style="color:#a6adc8;min-width:55px;">Yiyecek:</label><input id="wg-threshold-food" type="number" min="0" value="0" data-resource="food" style="width:90px;background:#313244;color:#cdd6f4;border:1px solid #45475a;border-radius:4px;padding:4px 6px;"></div>
              </div>
            </div>
            <div id="wg-progress" style="color:#a6adc8;font-size:12px;margin-top:4px;">Hedef: —</div>
          </div>
        </div>

        <div id="wg-content-alliance" style="display:none;padding:32px 16px;text-align:center;">
          <div style="font-size:32px;margin-bottom:12px;">🗺️</div>
          <div style="color:#89b4fa;font-size:15px;font-weight:bold;margin-bottom:8px;">İttifak Lokasyon</div>
          <div style="color:#6c7086;font-size:13px;">Yakında eklenecektir...</div>
        </div>
      </div>
    `;
    document.body.appendChild(panel);
    _bindEvents(panel, _callbacks);
    _bindDrag(panel);
    return panel;
  }

  function _bindEvents(panel, callbacks) {
    const startBtn = panel.querySelector('#wg-start');
    const stopBtn = panel.querySelector('#wg-stop');
    const refreshBtn = panel.querySelector('#wg-refresh');
    const intervalInput = panel.querySelector('#wg-interval');
    const minimizeBtn = panel.querySelector('#wg-minimize');
    const body = panel.querySelector('#wg-body');

    if (startBtn && callbacks.onStart) startBtn.addEventListener('click', () => callbacks.onStart());
    if (stopBtn && callbacks.onStop) stopBtn.addEventListener('click', () => callbacks.onStop());
    if (refreshBtn && callbacks.onRefresh) refreshBtn.addEventListener('click', () => callbacks.onRefresh());
    if (intervalInput && callbacks.onIntervalChange) {
      intervalInput.addEventListener('change', () => callbacks.onIntervalChange(parseInt(intervalInput.value, 10)));
    }
    if (minimizeBtn && body) {
      minimizeBtn.addEventListener('click', () => {
        const isHidden = body.style.display === 'none';
        body.style.display = isHidden ? '' : 'none';
        minimizeBtn.textContent = isHidden ? '−' : '+';
      });
    }
    const closeBtn = panel.querySelector('#wg-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        stopTracker();
        panel.remove();
      });
    }

    // Dil butonları
    const langTrBtn = panel.querySelector('#wg-lang-tr');
    const langEnBtn = panel.querySelector('#wg-lang-en');
    function updateLangButtons(activeLang) {
      if (langTrBtn) {
        langTrBtn.style.background = activeLang === 'tr' ? '#89b4fa' : '#313244';
        langTrBtn.style.color = activeLang === 'tr' ? '#1e1e2e' : '#cdd6f4';
        langTrBtn.style.border = activeLang === 'tr' ? 'none' : '1px solid #45475a';
      }
      if (langEnBtn) {
        langEnBtn.style.background = activeLang === 'en' ? '#89b4fa' : '#313244';
        langEnBtn.style.color = activeLang === 'en' ? '#1e1e2e' : '#cdd6f4';
        langEnBtn.style.border = activeLang === 'en' ? 'none' : '1px solid #45475a';
      }
    }
    if (langTrBtn) {
      langTrBtn.addEventListener('click', () => {
        setLanguage('tr');
        updateLangButtons('tr');
        rerenderTexts();
      });
    }
    if (langEnBtn) {
      langEnBtn.addEventListener('click', () => {
        setLanguage('en');
        updateLangButtons('en');
        rerenderTexts();
      });
    }
    // Başlangıçta aktif dile göre butonları ayarla
    updateLangButtons(getLanguage());

    // Sekme geçişi
    const tabResources = panel.querySelector('#wg-tab-resources');
    const tabAlliance = panel.querySelector('#wg-tab-alliance');
    const contentResources = panel.querySelector('#wg-content-resources');
    const contentAlliance = panel.querySelector('#wg-content-alliance');
    if (tabResources && tabAlliance) {
      tabResources.addEventListener('click', () => {
        contentResources.style.display = '';
        contentAlliance.style.display = 'none';
        tabResources.style.background = '#1e1e2e';
        tabResources.style.color = '#89b4fa';
        tabResources.style.borderBottom = '2px solid #89b4fa';
        tabAlliance.style.background = '#181825';
        tabAlliance.style.color = '#6c7086';
        tabAlliance.style.borderBottom = '2px solid transparent';
      });
      tabAlliance.addEventListener('click', () => {
        contentResources.style.display = 'none';
        contentAlliance.style.display = '';
        tabAlliance.style.background = '#1e1e2e';
        tabAlliance.style.color = '#89b4fa';
        tabAlliance.style.borderBottom = '2px solid #89b4fa';
        tabResources.style.background = '#181825';
        tabResources.style.color = '#6c7086';
        tabResources.style.borderBottom = '2px solid transparent';
      });
    }

    const modeRadios = panel.querySelectorAll('input[name="wg-alarm-mode"]');
    modeRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        _updateAlarmModeVisibility(radio.value);
        if (callbacks.onAlarmModeChange) callbacks.onAlarmModeChange(radio.value);
      });
    });
    const grandTarget = panel.querySelector('#wg-grand-target');
    if (grandTarget && callbacks.onThresholdChange) {
      grandTarget.addEventListener('change', () => callbacks.onThresholdChange('grandTotal', parseInt(grandTarget.value, 10) || 0));
    }
    const resourceInputs = panel.querySelectorAll('[data-resource]');
    resourceInputs.forEach(input => {
      if (callbacks.onThresholdChange) {
        input.addEventListener('change', () => callbacks.onThresholdChange(input.dataset.resource, parseInt(input.value, 10) || 0));
      }
    });
  }

  function _updateAlarmModeVisibility(mode) {
    const grandRow = document.getElementById('wg-grand-input-row');
    const perRow = document.getElementById('wg-per-resource-inputs');
    if (!grandRow || !perRow) return;
    if (mode === 'grand_total') {
      grandRow.style.display = 'flex';
      perRow.style.display = 'none';
    } else {
      grandRow.style.display = 'none';
      perRow.style.display = '';
    }
  }

  function _bindDrag(panel) {
    const header = panel.querySelector('#wg-header');
    if (!header) return;
    let isDragging = false, startX = 0, startY = 0, startLeft = 0, startTop = 0;
    function getPos(e) {
      if (e.touches && e.touches.length > 0) return { x: e.touches[0].clientX, y: e.touches[0].clientY };
      return { x: e.clientX, y: e.clientY };
    }
    function onDragStart(e) {
      if (e.target.tagName === 'BUTTON') return;
      isDragging = true;
      const pos = getPos(e);
      startX = pos.x; startY = pos.y;
      const rect = panel.getBoundingClientRect();
      startLeft = rect.left; startTop = rect.top;
      panel.style.right = 'auto';
      panel.style.left = startLeft + 'px';
      panel.style.top = startTop + 'px';
      e.preventDefault();
    }
    function onDragMove(e) {
      if (!isDragging) return;
      const pos = getPos(e);
      panel.style.left = (startLeft + pos.x - startX) + 'px';
      panel.style.top = (startTop + pos.y - startY) + 'px';
      e.preventDefault();
    }
    function onDragEnd() { isDragging = false; }
    header.addEventListener('mousedown', onDragStart);
    document.addEventListener('mousemove', onDragMove);
    document.addEventListener('mouseup', onDragEnd);
    header.addEventListener('touchstart', onDragStart, { passive: false });
    document.addEventListener('touchmove', onDragMove, { passive: false });
    document.addEventListener('touchend', onDragEnd);
  }

  function renderTable(villages, totals) {
    const tbody = document.getElementById('wg-table-body');
    if (!tbody) return;
    if (!villages || villages.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:8px;color:#6c7086;">${t('no_data')}</td></tr>`;
      return;
    }
    tbody.innerHTML = '';
    villages.forEach(v => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid #313244';
      [{ text: v.name, align: 'left' }, { text: formatNumber(v.wood), align: 'right' }, { text: formatNumber(v.clay), align: 'right' }, { text: formatNumber(v.iron), align: 'right' }, { text: formatNumber(v.food), align: 'right' }, { text: formatNumber(v.rowTotal), align: 'right' }].forEach(({ text, align }) => {
        const td = document.createElement('td');
        td.style.cssText = `text-align:${align};padding:4px 6px;`;
        td.textContent = text;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    if (totals) {
      const grandTotal = totals.grandTotal !== undefined ? totals.grandTotal : (totals.wood + totals.clay + totals.iron + totals.food);
      const tr = document.createElement('tr');
      tr.style.cssText = 'border-top:2px solid #45475a;font-weight:bold;color:#89b4fa;';
      [{ text: t('total_row'), align: 'left' }, { text: formatNumber(totals.wood), align: 'right' }, { text: formatNumber(totals.clay), align: 'right' }, { text: formatNumber(totals.iron), align: 'right' }, { text: formatNumber(totals.food), align: 'right' }, { text: formatNumber(grandTotal), align: 'right' }].forEach(({ text, align }) => {
        const td = document.createElement('td');
        td.style.cssText = `text-align:${align};padding:4px 6px;`;
        td.textContent = text;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    }
  }

  function renderControls(state) {
    const startBtn = document.getElementById('wg-start');
    const stopBtn = document.getElementById('wg-stop');
    const refreshBtn = document.getElementById('wg-refresh');
    const lastUpdate = document.getElementById('wg-last-update');
    if (startBtn) {
      startBtn.disabled = !!state.isRunning;
      startBtn.style.opacity = state.isRunning ? '0.4' : '1';
      startBtn.style.cursor = state.isRunning ? 'not-allowed' : 'pointer';
      startBtn.textContent = t('btn_start');
    }
    if (stopBtn) {
      stopBtn.disabled = !state.isRunning;
      stopBtn.style.opacity = !state.isRunning ? '0.4' : '1';
      stopBtn.style.cursor = !state.isRunning ? 'not-allowed' : 'pointer';
      stopBtn.textContent = t('btn_stop');
    }
    if (refreshBtn) {
      if (state.isRefreshing) { refreshBtn.textContent = t('btn_refreshing'); refreshBtn.disabled = true; refreshBtn.style.opacity = '0.4'; }
      else { refreshBtn.textContent = t('btn_refresh'); refreshBtn.disabled = false; refreshBtn.style.opacity = '1'; }
    }
    if (lastUpdate && state.lastUpdated) {
      const date = typeof state.lastUpdated === 'string' ? new Date(state.lastUpdated) : state.lastUpdated;
      lastUpdate.textContent = `${t('label_last_update')}: ${formatTime(date)}`;
    }
  }

  function renderProgress(current, target, alarmMode, thresholds, totals) {
    const progressEl = document.getElementById('wg-progress');
    if (!progressEl) return;

    let effectiveTarget;
    if (alarmMode === 'per_resource') {
      effectiveTarget = (thresholds.wood||0) + (thresholds.clay||0) + (thresholds.iron||0) + (thresholds.food||0);
    } else {
      effectiveTarget = thresholds.grandTotal || 0;
    }

    if (!effectiveTarget || effectiveTarget <= 0) {
      progressEl.textContent = t('target_none');
      progressEl.style.color = '#a6adc8';
      return;
    }

    const currentTotal = totals ? totals.grandTotal : 0;
    const pct = calculateProgress(currentTotal, effectiveTarget);
    const reached = currentTotal >= effectiveTarget;
    progressEl.style.color = reached ? '#a6e3a1' : '#f9e2af';
    const progressText = t('target_progress')
      .replace('{pct}', pct)
      .replace('%{pct}', pct)
      .replace('{current}', formatNumber(currentTotal))
      .replace('{target}', formatNumber(effectiveTarget));
    progressEl.textContent = progressText;
  }

  function rerenderTexts() {
    const panel = document.getElementById('wg-tracker-panel');
    if (!panel) return;

    // Panel başlığı
    const titleEl = panel.querySelector('#wg-panel-title');
    if (titleEl) titleEl.textContent = t('panel_title');

    // Sekmeler
    const tabRes = panel.querySelector('#wg-tab-resources');
    if (tabRes) tabRes.textContent = t('tab_resources');
    const tabAll = panel.querySelector('#wg-tab-alliance');
    if (tabAll) tabAll.textContent = t('tab_alliance');

    // Tablo başlıkları
    const thead = panel.querySelector('#wg-resource-table thead tr');
    if (thead) {
      const ths = thead.querySelectorAll('th');
      const keys = ['col_village','col_wood','col_clay','col_iron','col_food','col_total'];
      ths.forEach((th, i) => { if (keys[i]) th.textContent = t(keys[i]); });
    }

    // Kontrol butonları
    const startBtn = panel.querySelector('#wg-start');
    if (startBtn && !startBtn.disabled) startBtn.textContent = t('btn_start');
    const stopBtn = panel.querySelector('#wg-stop');
    if (stopBtn && !stopBtn.disabled) stopBtn.textContent = t('btn_stop');
    const refreshBtn = panel.querySelector('#wg-refresh');
    if (refreshBtn && !refreshBtn.disabled) refreshBtn.textContent = t('btn_refresh');

    // Aralık etiketi
    const intervalLabels = panel.querySelectorAll('label');
    intervalLabels.forEach(lbl => {
      if (lbl.textContent.trim() === 'Aralık:' || lbl.textContent.trim() === 'Interval:') {
        lbl.textContent = t('label_interval') + ':';
      }
    });
    const intervalUnitSpans = panel.querySelectorAll('span');
    intervalUnitSpans.forEach(sp => {
      if (sp.textContent.trim() === 'sn' || sp.textContent.trim() === 'sec') {
        sp.textContent = t('label_interval_unit');
      }
    });

    // Son güncelleme
    const lastUpdateEl = panel.querySelector('#wg-last-update');
    if (lastUpdateEl && appState.lastUpdated) {
      const date = typeof appState.lastUpdated === 'string' ? new Date(appState.lastUpdated) : appState.lastUpdated;
      lastUpdateEl.textContent = `${t('label_last_update')}: ${formatTime(date)}`;
    } else if (lastUpdateEl) {
      lastUpdateEl.textContent = `${t('label_last_update')}: —`;
    }

    // Alarm modu etiketleri
    const modeGrandLabel = panel.querySelector('label[for="wg-mode-grand"], label:has(#wg-mode-grand)');
    const modePerLabel = panel.querySelector('label[for="wg-mode-per"], label:has(#wg-mode-per)');
    panel.querySelectorAll('label').forEach(lbl => {
      const radio = lbl.querySelector('input[type="radio"]');
      if (!radio) return;
      if (radio.value === 'grand_total') {
        // preserve the radio input, update text node
        const textNode = Array.from(lbl.childNodes).find(n => n.nodeType === Node.TEXT_NODE);
        if (textNode) textNode.textContent = ' ' + t('mode_grand_total');
      } else if (radio.value === 'per_resource') {
        const textNode = Array.from(lbl.childNodes).find(n => n.nodeType === Node.TEXT_NODE);
        if (textNode) textNode.textContent = ' ' + t('mode_per_resource');
      }
    });

    // Hedef etiketi
    const grandTargetLabel = panel.querySelector('#wg-grand-input-row label');
    if (grandTargetLabel) grandTargetLabel.textContent = t('label_target') + ':';

    // Kaynak etiketleri
    const resourceLabelMap = { wood: 'label_wood', clay: 'label_clay', iron: 'label_iron', food: 'label_food' };
    panel.querySelectorAll('[data-resource]').forEach(input => {
      const res = input.dataset.resource;
      const lbl = input.closest('div') && input.closest('div').querySelector('label');
      if (lbl && resourceLabelMap[res]) lbl.textContent = t(resourceLabelMap[res]) + ':';
    });

    // İttifak içerik
    const allianceTitleEl = panel.querySelector('#wg-content-alliance div:nth-child(2)');
    if (allianceTitleEl) allianceTitleEl.textContent = t('alliance_title');
    const comingSoonEl = panel.querySelector('#wg-content-alliance div:nth-child(3)');
    if (comingSoonEl) comingSoonEl.textContent = t('coming_soon');

    // Tablo içeriğini yeniden render et (metinler için)
    renderTable(appState.villages, appState.totals);
    renderProgress(appState.totals ? appState.totals.grandTotal : 0, null, appState.alarmMode, appState.thresholds, appState.totals);
  }

  // ─── app ─────────────────────────────────────────────────────────────────────

  function showPopup(message) {
    const existing = document.getElementById('wg-popup-overlay');
    if (existing) existing.remove();
    const overlay = document.createElement('div');
    overlay.id = 'wg-popup-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999999;display:flex;align-items:center;justify-content:center;';
    const dialog = document.createElement('div');
    dialog.id = 'wg-popup-dialog';
    dialog.style.cssText = 'background:#1e1e2e;color:#cdd6f4;border:1px solid #89b4fa;border-radius:8px;padding:24px;max-width:400px;width:90%;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.8);';
    dialog.innerHTML = `<div style="font-size:32px;margin-bottom:12px;">🎯</div><div style="font-size:16px;font-weight:bold;margin-bottom:16px;">${message}</div><button id="wg-popup-close" style="background:#89b4fa;color:#1e1e2e;border:none;border-radius:4px;padding:0 24px;min-height:44px;cursor:pointer;font-weight:bold;font-size:14px;">Tamam</button>`;
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    const closeBtn = overlay.querySelector('#wg-popup-close');
    if (closeBtn) closeBtn.addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
  }

  // ─── AppState ────────────────────────────────────────────────────────────────

  let appState = {
    isRunning: false,
    isRefreshing: false,
    lastUpdated: null,
    villages: [],
    totals: null,
    intervalSecs: 60,
    alarmMode: 'grand_total',
    thresholds: { wood: 0, clay: 0, iron: 0, food: 0, grandTotal: 0 },
    alarmFired: false,
    lastError: null,
  };

  // ─── Callbacks ───────────────────────────────────────────────────────────────

  function onData(villages, totals) {
    appState.villages = villages;
    appState.totals = totals;
    appState.lastUpdated = new Date().toISOString();
    renderTable(villages, totals);
    renderControls(appState);
    // İlerleme göstergesini güncelle
    renderProgress(totals.grandTotal, null, appState.alarmMode, appState.thresholds, totals);
    saveVillageData(villages, appState.lastUpdated);
    const alarmResult = checkAlarm(totals, appState.thresholds, appState.alarmMode, appState.alarmFired);
    if (alarmResult.triggered) {
      appState.alarmFired = true;
      stopTracker();
      appState.isRunning = false;
      renderControls(appState);
      playAlarmSound();
      sendNotification('🎯 Hedefe ulaşıldı!');
      showPopup('🎯 Hedefe ulaşıldı! Otomatik yenileme durduruldu.');
    }
  }

  function onError(errorObj) {
    appState.lastError = errorObj;
    console.warn('[WG Tracker]', errorObj.message);
  }

  // ─── init ────────────────────────────────────────────────────────────────────

  function init() {
    loadLanguage();
    const settings = loadSettings();
    appState.intervalSecs = settings.intervalSecs;
    appState.alarmMode = settings.alarmMode;
    appState.thresholds = settings.thresholds;

    const saved = loadVillageData();
    if (saved.villages && saved.villages.length > 0) {
      appState.villages = saved.villages;
      appState.lastUpdated = saved.lastUpdated;
    }

    const callbacks = {
      onStart: () => {
        startTracker(appState.intervalSecs, onData, onError);
        appState.isRunning = true;
        renderControls(appState);
      },
      onStop: () => {
        stopTracker();
        appState.isRunning = false;
        appState.alarmFired = false;
        renderControls(appState);
      },
      onRefresh: () => {
        _runCycle(onData, onError);
      },
      onIntervalChange: (val) => {
        const validated = validateInterval(val);
        appState.intervalSecs = validated;
        saveSettings({ intervalSecs: appState.intervalSecs, alarmMode: appState.alarmMode, thresholds: appState.thresholds });
      },
      onAlarmModeChange: (mode) => {
        appState.alarmMode = mode;
        appState.alarmFired = false;
        saveSettings({ intervalSecs: appState.intervalSecs, alarmMode: appState.alarmMode, thresholds: appState.thresholds });
      },
      onThresholdChange: (key, value) => {
        appState.thresholds[key] = value;
        appState.alarmFired = false;
        saveSettings({ intervalSecs: appState.intervalSecs, alarmMode: appState.alarmMode, thresholds: appState.thresholds });
      },
    };

    createPanel(callbacks);
    renderTable(appState.villages, appState.totals);
    renderControls(appState);

    const intervalInput = document.getElementById('wg-interval');
    if (intervalInput) intervalInput.value = appState.intervalSecs;
  }

  init();

})();
