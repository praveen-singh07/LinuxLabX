const TOKEN_KEY = 'linuxlabx_access_token';
const LAST_UNLOCKS_PREFIX = 'linuxlabx_seen_badges_';
const authForm = document.querySelector('#auth-form');
const authMessage = document.querySelector('#auth-message');
const authPanel = document.querySelector('#auth-panel');
const dashboard = document.querySelector('#dashboard-content');
const collection = document.querySelector('#collection');
const badgeGrid = document.querySelector('#badge-grid');
const pageMessage = document.querySelector('#page-message');
const authToggle = document.querySelector('#auth-toggle');
const nameField = document.querySelector('#name-field');
const pathGrid = document.querySelector('#path-grid');
const lessonDialog = document.querySelector('#lesson-dialog');
let registerMode = false;
let currentLesson = null;
let completedLessonIds = new Set();

function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

async function api(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers = { ...(options.headers || {}) };
  if (options.body) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(path, { ...options, headers });
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(payload?.detail || 'Request could not be completed.');
  return payload;
}

authToggle.addEventListener('click', () => {
  registerMode = !registerMode;
  nameField.classList.toggle('is-hidden', !registerMode);
  nameField.querySelector('input').required = registerMode;
  authForm.querySelector('[name="password"]').autocomplete = registerMode ? 'new-password' : 'current-password';
  document.querySelector('#auth-title').textContent = registerMode ? 'Create your LinuxLabX account' : 'Sign in to your dashboard';
  document.querySelector('#auth-submit').textContent = registerMode ? 'Create account' : 'Sign in';
  authToggle.textContent = registerMode ? 'I already have an account' : 'Create account';
  authMessage.textContent = '';
});

authForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  authMessage.textContent = '';
  authMessage.style.color = '#ff9f9f';
  const data = Object.fromEntries(new FormData(authForm).entries());
  try {
    if (registerMode) {
      await api('/auth/register', { method: 'POST', body: JSON.stringify(data) });
      registerMode = false;
      nameField.classList.add('is-hidden');
      nameField.querySelector('input').required = false;
      document.querySelector('#auth-title').textContent = 'Account created — sign in';
      document.querySelector('#auth-submit').textContent = 'Sign in';
      authToggle.textContent = 'Create account';
      authMessage.style.color = '#9de3b3';
      authMessage.textContent = 'Account created. Sign in with your new details.';
      return;
    }
    const result = await api('/auth/login', { method: 'POST', body: JSON.stringify(data) });
    localStorage.setItem(TOKEN_KEY, result.access_token);
    authForm.reset();
    await loadDashboard(true);
  } catch (error) {
    authMessage.textContent = error.message;
  }
});

document.querySelector('#logout-button').addEventListener('click', () => {
  localStorage.removeItem(TOKEN_KEY);
  dashboard.classList.add('is-hidden');
  collection.classList.add('is-hidden');
  authPanel.classList.remove('is-hidden');
  document.querySelector('#unlocked-count').textContent = '—';
});

document.querySelector('.dialog-close').addEventListener('click', () => document.querySelector('#unlock-dialog').close());
document.querySelector('.lesson-close').addEventListener('click', () => lessonDialog.close());
document.querySelector('#complete-lesson-button').addEventListener('click', completeCurrentLesson);

pathGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-path-id]');
  if (!button) return;
  const pathCard = button.closest('.path-card');
  const detail = pathCard.querySelector('.path-detail');
  if (detail) {
    detail.classList.toggle('is-hidden');
    button.textContent = detail.classList.contains('is-hidden') ? 'Explore path' : 'Hide lessons';
    return;
  }
  button.disabled = true;
  button.textContent = 'Loading…';
  try {
    const path = await api(`/learning-paths/${button.dataset.pathId}`);
    const panel = document.createElement('div');
    panel.className = 'path-detail';
    panel.innerHTML = path.topics.length ? path.topics.map((topic) => `
      <section class="topic-block">
        <h4>${escapeHTML(topic.title)}</h4>
        ${topic.description ? `<p>${escapeHTML(topic.description)}</p>` : ''}
        ${topic.lessons.length ? topic.lessons.map((lesson) => {
          const done = completedLessonIds.has(lesson.id);
          return `<button class="lesson-link ${done ? 'is-complete' : ''}" type="button" data-lesson-id="${lesson.id}">
            <span>${escapeHTML(lesson.title)}</span><small>${done ? '✓ Completed' : escapeHTML(lesson.difficulty)}</small>
          </button>`;
        }).join('') : '<p>No published lessons in this topic yet.</p>'}
      </section>`).join('') : '<p>This path has no published topics yet.</p>';
    pathCard.append(panel);
    button.disabled = false;
    button.textContent = 'Hide lessons';
  } catch (error) {
    button.disabled = false;
    button.textContent = 'Try again';
    pageMessage.textContent = error.message;
  }
});

pathGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-lesson-id]');
  if (!button) return;
  const lessonId = Number(button.dataset.lessonId);
  try {
    currentLesson = await api(`/lessons/${lessonId}`);
    showLesson(currentLesson);
  } catch (error) {
    pageMessage.textContent = error.message;
  }
});

function renderBadges(items) {
  badgeGrid.innerHTML = items.map((badge) => `
    <article class="badge-card ${badge.unlocked ? 'is-unlocked' : 'is-locked'}" data-code="${escapeHTML(badge.code)}">
      <div class="badge-art-wrap"><img class="badge-art" src="${escapeHTML(badge.icon_path)}" alt="${escapeHTML(badge.title)} medal artwork"></div>
      <h3 class="badge-title">${escapeHTML(badge.title)}</h3>
      <p class="badge-description">${escapeHTML(badge.unlocked ? badge.description : badge.criteria)}</p>
      <span class="badge-status">${badge.unlocked ? '✓ Unlocked' : '⌑ Locked'}</span>
    </article>`).join('');
}

function renderPaths(paths) {
  document.querySelector('#path-count').textContent = `${paths.length} ${paths.length === 1 ? 'path' : 'paths'}`;
  document.querySelector('#path-empty').classList.toggle('is-hidden', paths.length > 0);
  pathGrid.innerHTML = paths.map((path, index) => `
    <article class="path-card">
      <div class="path-card-top"><span class="path-index">PATH ${String(index + 1).padStart(2, '0')}</span><span class="muted-label">${path.topics_count} ${path.topics_count === 1 ? 'topic' : 'topics'}</span></div>
      <h3>${escapeHTML(path.title)}</h3>
      <p>${escapeHTML(path.description || 'A guided path to build your Linux skills.')}</p>
      <button class="button path-open" type="button" data-path-id="${path.id}">Explore path</button>
    </article>`).join('');
}

function showLesson(lesson) {
  document.querySelector('#lesson-content').innerHTML = `
    <p class="eyebrow">${escapeHTML(lesson.difficulty)} LESSON</p>
    <h2>${escapeHTML(lesson.title)}</h2>
    ${lesson.description ? `<p>${escapeHTML(lesson.description)}</p>` : ''}
    ${lesson.command ? `<div class="lesson-command">$ ${escapeHTML(lesson.command)}</div>` : ''}
    ${lesson.syntax ? `<p><strong>Syntax:</strong> <code>${escapeHTML(lesson.syntax)}</code></p>` : ''}
    ${(lesson.examples || []).map((example) => `<div class="lesson-example"><strong>$ ${escapeHTML(example.command || lesson.command || '')}</strong><pre>${escapeHTML(example.output || '')}</pre></div>`).join('')}
    ${lesson.expected_output ? `<p><strong>Expected output:</strong></p><div class="lesson-command">${escapeHTML(lesson.expected_output)}</div>` : ''}
    ${lesson.tips?.length ? `<p><strong>Tips</strong></p><ul class="lesson-list">${lesson.tips.map((tip) => `<li>${escapeHTML(tip)}</li>`).join('')}</ul>` : ''}
    ${lesson.common_mistakes?.length ? `<p><strong>Common mistakes</strong></p><ul class="lesson-list">${lesson.common_mistakes.map((tip) => `<li>${escapeHTML(tip)}</li>`).join('')}</ul>` : ''}`;
  const done = completedLessonIds.has(lesson.id);
  const button = document.querySelector('#complete-lesson-button');
  button.disabled = done;
  button.textContent = done ? 'Lesson completed ✓' : 'Mark lesson complete';
  document.querySelector('#lesson-completion-result').textContent = '';
  lessonDialog.showModal();
}

async function completeCurrentLesson() {
  if (!currentLesson) return;
  const button = document.querySelector('#complete-lesson-button');
  const resultText = document.querySelector('#lesson-completion-result');
  button.disabled = true;
  button.textContent = 'Saving…';
  try {
    const result = await api(`/lessons/${currentLesson.id}/complete`, { method: 'POST' });
    completedLessonIds.add(currentLesson.id);
    resultText.textContent = result.already_completed ? 'This lesson was already completed.' : `Lesson completed · +${result.xp_awarded} XP`;
    button.textContent = 'Lesson completed ✓';
    const newBadges = result.newly_unlocked || [];
    await loadDashboard(false);
    if (newBadges.length) {
      window.setTimeout(() => celebrateBadges(newBadges), 250);
    }
  } catch (error) {
    button.disabled = false;
    button.textContent = 'Mark lesson complete';
    resultText.style.color = '#ff9f9f';
    resultText.textContent = error.message;
  }
}

function celebrateBadges(badges) {
  if (!badges.length) return;
  const first = badges[0];
  const dialog = document.querySelector('#unlock-dialog');
  document.querySelector('#unlock-content').innerHTML = `
    <img src="${escapeHTML(first.icon_path)}" alt="${escapeHTML(first.title)} badge">
    <p class="eyebrow">${badges.length > 1 ? `${badges.length} NEW BADGES` : 'NEW ACHIEVEMENT'}</p>
    <h2>${escapeHTML(first.title)}${badges.length > 1 ? ` + ${badges.length - 1}` : ''}</h2>
    <p>${escapeHTML(first.description)}</p>`;
  dialog.showModal();
}

async function loadDashboard(celebrateNew = false) {
  pageMessage.textContent = '';
  try {
    const [profile, summary, paths, completions, badges] = await Promise.all([
      api('/auth/me'), api('/dashboard'), api('/learning-paths'),
      api('/lessons/completed/me'), api('/achievements/me'),
    ]);
    authPanel.classList.add('is-hidden');
    dashboard.classList.remove('is-hidden');
    collection.classList.remove('is-hidden');
    document.querySelector('#welcome-title').textContent = `Welcome, ${profile.name}`;
    document.querySelector('#collection-title').textContent = `${profile.name}'s collection`;
    document.querySelector('#stat-xp').textContent = `${summary.xp.total_xp} XP`;
    document.querySelector('#stat-level').textContent = `Level ${summary.xp.level}`;
    document.querySelector('#stat-lessons').textContent = summary.progress.lessons_completed;
    document.querySelector('#stat-practice').textContent = summary.progress.practice_completed;
    document.querySelector('#stat-activities').textContent = summary.progress.quizzes_completed + summary.progress.challenges_completed;
    const progress = Math.max(0, Math.min(100, summary.progress.progress_percentage));
    document.querySelector('#progress-label').textContent = `${progress}%`;
    document.querySelector('#progress-fill').style.width = `${progress}%`;
    document.querySelector('#last-activity').textContent = summary.progress.last_activity || 'Complete a lesson to start tracking your progress.';
    completedLessonIds = new Set(completions.map((item) => item.lesson_id));
    renderPaths(paths);
    renderBadges(badges.achievements);
    document.querySelector('#unlocked-count').textContent = `${badges.unlocked_count}/${badges.total}`;
    document.querySelector('#achievement-summary').textContent = `${badges.unlocked_count} of ${badges.total} badges unlocked. Your locked badges show what to work toward next.`;

    const storageKey = LAST_UNLOCKS_PREFIX + profile.id;
    const current = badges.achievements.filter((item) => item.unlocked).map((item) => item.code);
    const previous = localStorage.getItem(storageKey);
    if (celebrateNew && previous !== null) {
      const previousCodes = new Set(JSON.parse(previous));
      const newBadges = badges.achievements.filter((item) => item.unlocked && !previousCodes.has(item.code));
      newBadges.forEach((item) => pathGrid.ownerDocument.querySelector(`#collection [data-code="${CSS.escape(item.code)}"]`)?.classList.add('is-new'));
      celebrateBadges(newBadges);
    }
    localStorage.setItem(storageKey, JSON.stringify(current));
  } catch (error) {
    localStorage.removeItem(TOKEN_KEY);
    dashboard.classList.add('is-hidden');
    collection.classList.add('is-hidden');
    authPanel.classList.remove('is-hidden');
    authMessage.textContent = error.message;
  }
}

if (localStorage.getItem(TOKEN_KEY)) loadDashboard(true);
