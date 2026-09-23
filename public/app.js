/**
 * AI Morning Digest - PWA フロントエンドロジック
 */

// グローバル状態
let newsData = null;
let currentDayArticles = [];
let activeCategory = 'all';
let searchQuery = '';
let readArticleIds = new Set(JSON.parse(localStorage.getItem('read_articles') || '[]'));

// DOM要素
const newsContainer = document.getElementById('news-list');
const dateTabsContainer = document.getElementById('date-tabs');
const updateTimeEl = document.getElementById('update-time');
const searchInput = document.getElementById('search-input');
const categoryChips = document.querySelectorAll('.cat-chip');
const themeToggleBtn = document.getElementById('theme-toggle');
const offlineBanner = document.getElementById('offline-banner');
const pwaPrompt = document.getElementById('pwa-prompt');
const pwaCloseBtn = document.getElementById('pwa-close-btn');

// 1. 初期化
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  registerServiceWorker();
  initNetworkListeners();
  initPwaBanner();
  fetchNewsData();

  // 検索入力イベント
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase().trim();
    renderArticles();
  });

  // カテゴリチップの切り替え
  categoryChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      categoryChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      activeCategory = chip.dataset.category;
      renderArticles();
    });
  });

  // テーマ切り替え
  themeToggleBtn.addEventListener('click', toggleTheme);
});

// 2. ニュースデータの取得
async function fetchNewsData() {
  try {
    const res = await fetch('./data/news.json?t=' + Date.now());
    if (!res.ok) throw new Error('Network error');
    newsData = await res.json();
    setupDataView(newsData);
  } catch (err) {
    console.warn('Fetching news.json failed, falling back to cache...', err);
    // Service Worker からのキャッシュ取得を期待
    try {
      const cached = await fetch('./data/news.json');
      newsData = await cached.json();
      setupDataView(newsData);
    } catch (cacheErr) {
      showError('ニュースデータを読み込めませんでした。後ほど再度お試しください。');
    }
  }
}

// 3. データと日付タブの初期描画
function setupDataView(data) {
  if (!data || !data.current) {
    showError('表示できるニュースがまだありません。');
    return;
  }

  // 最終更新日時の表示
  updateTimeEl.textContent = `更新: ${data.meta.last_updated_jst || '本日'}`;

  // 日付タブの生成（最新 + 過去ログ）
  dateTabsContainer.innerHTML = '';
  
  // 今日のタブ
  const currentTab = createDateTab(data.current.date + ' (最新)', true, () => {
    selectDayData(data.current.articles);
  });
  dateTabsContainer.appendChild(currentTab);

  // 過去アーカイブのタブ
  if (data.archives && data.archives.length > 0) {
    data.archives.forEach((arch) => {
      const tab = createDateTab(arch.date, false, () => {
        selectDayData(arch.articles);
      });
      dateTabsContainer.appendChild(tab);
    });
  }

  // 初期選択（最新日）
  selectDayData(data.current.articles);
}

function createDateTab(label, isActive, onClick) {
  const btn = document.createElement('button');
  btn.className = `date-tab ${isActive ? 'active' : ''}`;
  btn.textContent = label;
  btn.addEventListener('click', () => {
    document.querySelectorAll('.date-tab').forEach((t) => t.classList.remove('active'));
    btn.classList.add('active');
    onClick();
  });
  return btn;
}

function selectDayData(articles) {
  currentDayArticles = articles || [];
  renderArticles();
}

// 4. 記事カードのレンダリング
function renderArticles() {
  newsContainer.innerHTML = '';

  // フィルタリング（カテゴリ & 検索）
  const filtered = currentDayArticles.filter((item) => {
    const matchCategory =
      activeCategory === 'all' ||
      (item.category && item.category.includes(activeCategory));

    const matchSearch =
      !searchQuery ||
      item.japanese_title.toLowerCase().includes(searchQuery) ||
      (item.original_title && item.original_title.toLowerCase().includes(searchQuery)) ||
      (item.summary_points && item.summary_points.some((p) => p.toLowerCase().includes(searchQuery))) ||
      (item.keywords && item.keywords.some((k) => k.toLowerCase().includes(searchQuery)));

    return matchCategory && matchSearch;
  });

  if (filtered.length === 0) {
    newsContainer.innerHTML = `
      <div class="empty-box">
        <p>条件に一致するニュースが見つかりませんでした。</p>
      </div>
    `;
    return;
  }

  filtered.forEach((item, index) => {
    const isRead = readArticleIds.has(item.link || item.japanese_title);
    const card = document.createElement('article');
    card.className = `news-card ${isRead ? 'read' : ''}`;

    // 重要度バッジ
    let importanceText = '★☆☆ 注目';
    if (item.importance === 3) importanceText = '★★★ 最重要';
    else if (item.importance === 2) importanceText = '★★☆ 注目';

    // 箇条書きポイント
    const pointsHtml = (item.summary_points || [])
      .map(
        (point) => `
        <li>
          <span class="summary-bullet">▸</span>
          <span>${escapeHtml(point)}</span>
        </li>
      `
      )
      .join('');

    // キーワードタグ
    const keywordsHtml = (item.keywords || [])
      .map((k) => `<span class="keyword-tag">#${escapeHtml(k)}</span>`)
      .join(' ');

    card.innerHTML = `
      <div class="card-meta-top">
        <span class="source-badge">${escapeHtml(item.source_name || 'News')}</span>
        <div class="card-tags-right">
          <span class="importance-badge">${importanceText}</span>
          <span class="read-time">${item.read_time_seconds || 30}秒</span>
        </div>
      </div>
      
      <h2 class="news-title">${escapeHtml(item.japanese_title)}</h2>
      
      <ul class="summary-points">
        ${pointsHtml}
      </ul>
      
      <div class="card-bottom">
        <div class="keywords-wrap">
          ${keywordsHtml}
        </div>
        <div class="card-actions">
          <button class="read-btn ${isRead ? 'is-read' : ''}" data-id="${escapeHtml(item.link || item.japanese_title)}">
            ${isRead ? '✓ 既読' : '未読'}
          </button>
          <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="link-btn">
            原文 ↗
          </a>
        </div>
      </div>
    `;

    // 既読トグルボタンのイベント
    const readBtn = card.querySelector('.read-btn');
    readBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleReadStatus(item.link || item.japanese_title, card, readBtn);
    });

    newsContainer.appendChild(card);
  });
}

function toggleReadStatus(id, cardEl, btnEl) {
  if (readArticleIds.has(id)) {
    readArticleIds.delete(id);
    cardEl.classList.remove('read');
    btnEl.classList.remove('is-read');
    btnEl.textContent = '未読';
  } else {
    readArticleIds.add(id);
    cardEl.classList.add('read');
    btnEl.classList.add('is-read');
    btnEl.textContent = '✓ 既読';
  }
  localStorage.setItem('read_articles', JSON.stringify([...readArticleIds]));
}

// 5. テーマ切替 (Dark/Light)
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  } else {
    // OSの好みを判定
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = prefersDark ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  themeToggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// 6. オフライン検出
function initNetworkListeners() {
  window.addEventListener('online', () => {
    offlineBanner.style.display = 'none';
  });
  window.addEventListener('offline', () => {
    offlineBanner.style.display = 'block';
  });
  if (!navigator.onLine) {
    offlineBanner.style.display = 'block';
  }
}

// 7. PWA案内バナー (iOS Safari向け)
function initPwaBanner() {
  const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;
  const dismissed = localStorage.getItem('pwa_prompt_dismissed');

  if (isIos && !isStandalone && !dismissed) {
    pwaPrompt.style.display = 'flex';
  }

  pwaCloseBtn.addEventListener('click', () => {
    pwaPrompt.style.display = 'none';
    localStorage.setItem('pwa_prompt_dismissed', 'true');
  });
}

// 8. Service Worker 登録
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js').catch((err) => {
        console.warn('ServiceWorker registration failed: ', err);
      });
    });
  }
}

function showError(msg) {
  newsContainer.innerHTML = `<div class="empty-box"><p>${msg}</p></div>`;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
