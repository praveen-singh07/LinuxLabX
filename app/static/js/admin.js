const ADMIN_TOKEN_KEY = 'linuxlabx_access_token';
const adminApp = document.querySelector('#admin-app');
const deniedPanel = document.querySelector('#admin-denied');
const typeSelect = document.querySelector('#content-type');
const listElement = document.querySelector('#content-list');
const formElement = document.querySelector('#content-form');
const messageElement = document.querySelector('#admin-message');
const topicPathFilter = document.querySelector('#topic-path-filter');
const topicPathSelect = document.querySelector('#topic-path');
const topicLinkPanel = document.querySelector('#topic-link-panel');
const linkTopicSelect = document.querySelector('#link-topic');
const linkLessonSelect = document.querySelector('#link-lesson');

const resources = {
  paths: {
    title: 'Learning paths', endpoint: '/admin/learning-paths', label: 'learning path',
    fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['display_order', 'Display order', 'number'], ['is_published', 'Published', 'checkbox'],
    ],
  },
  topics: {
    title: 'Topics', label: 'topic', fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['display_order', 'Display order', 'number'], ['is_published', 'Published', 'checkbox'],
    ],
  },
  lessons: {
    title: 'Lessons', endpoint: '/admin/lessons', label: 'lesson', fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['command', 'Command', 'text'], ['syntax', 'Syntax', 'textarea', true],
      ['examples', 'Examples (JSON array of {command, output})', 'json', true],
      ['expected_output', 'Expected output', 'textarea', true], ['options', 'Options (JSON array)', 'json', true],
      ['tips', 'Tips (JSON array)', 'json', true], ['common_mistakes', 'Common mistakes (JSON array)', 'json', true],
      ['difficulty', 'Difficulty', 'difficulty'], ['display_order', 'Display order', 'number'],
      ['is_published', 'Published', 'checkbox'],
    ],
  },
  quizzes: {
    title: 'Quizzes', endpoint: '/admin/quizzes', label: 'quiz', fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['difficulty', 'Difficulty', 'difficulty'], ['questions', 'Questions (JSON array: prompt, options, correct_option_index, explanation)', 'json', true],
      ['is_published', 'Published', 'checkbox'],
    ],
  },
  practice: {
    title: 'Practice exercises', endpoint: '/admin/practice', label: 'practice exercise', fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['instructions', 'Instructions', 'textarea', true], ['expected_answers', 'Accepted answers (JSON array)', 'json', true],
      ['difficulty', 'Difficulty', 'difficulty'], ['display_order', 'Display order', 'number'],
      ['is_published', 'Published', 'checkbox'],
    ],
  },
  challenges: {
    title: 'Challenges', endpoint: '/admin/challenges', label: 'challenge', fields: [
      ['title', 'Title', 'text', true], ['description', 'Description', 'textarea', true],
      ['scenario', 'Scenario', 'textarea', true], ['instructions', 'Instructions', 'textarea', true],
      ['expected_answers', 'Accepted answers (JSON array)', 'json', true], ['hints', 'Hints (JSON array)', 'json', true],
      ['difficulty', 'Difficulty', 'difficulty'], ['display_order', 'Display order', 'number'],
      ['is_published', 'Published', 'checkbox'],
    ],
  },
};

let currentItems = [];
let currentPaths = [];
let currentLessons = [];
let currentAdmin = null;
let currentUsers = [];
let usersOffset = 0;
const usersPageSize = 20;
let selectedId = null;

function safeText(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

async function adminApi(path, options = {}) {
  const headers = { ...(options.headers || {}), Authorization: `Bearer ${localStorage.getItem(ADMIN_TOKEN_KEY)}` };
  if (options.body) headers['Content-Type'] = 'application/json';
  const response = await fetch(path, { ...options, headers });
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.detail || 'Could not complete that request.');
  return body;
}

function announce(message, isError = false) {
  messageElement.textContent = message;
  messageElement.style.color = isError ? '#ff9f9f' : '#9de3b3';
}

function activeResource() { return resources[typeSelect.value]; }
function endpointFor(resource, id = null) {
  const base = typeSelect.value === 'topics'
    ? `/admin/learning-paths/${Number(topicPathSelect.value)}/topics`
    : resource.endpoint;
  return id === null ? base : (typeSelect.value === 'topics' ? `/admin/learning-paths/topics/${id}` : `${base}/${id}`);
}

async function loadTopicPaths() {
  currentPaths = await adminApi('/admin/learning-paths');
  topicPathSelect.innerHTML = currentPaths.map((item) => `<option value="${item.id}">${safeText(item.title)} · #${item.id}</option>`).join('');
  if (!currentPaths.length) topicPathSelect.innerHTML = '<option value="">Create a learning path first</option>';
}

function renderList() {
  const resource = activeResource();
  document.querySelector('#list-title').textContent = resource.title;
  document.querySelector('#list-count').textContent = `${currentItems.length} items`;
  document.querySelector('#content-total').textContent = String(currentItems.length);
  document.querySelector('#list-empty').classList.toggle('is-hidden', currentItems.length > 0);
  listElement.innerHTML = currentItems.map((item) => {
    const label = item.title || `Item ${item.id}`;
    const summary = `${resource.label} #${item.id} · ${item.difficulty || (item.display_order !== undefined ? `Order ${item.display_order}` : '')}`;
    return `<article class="admin-row ${selectedId === item.id ? 'is-selected' : ''}"><button class="admin-row-main" type="button" data-edit-id="${item.id}"><strong>${safeText(label)}</strong><span>${safeText(summary)}</span></button><span class="admin-badge ${item.is_published ? '' : 'is-draft'}">${item.is_published ? 'Live' : 'Draft'}</span></article>`;
  }).join('');
  if (typeSelect.value === 'topics') renderLinkOptions();
}

async function loadItems() {
  announce('');
  selectedId = null;
  formElement.classList.add('is-hidden');
  document.querySelector('#editor-empty').classList.remove('is-hidden');
  topicPathFilter.classList.toggle('is-hidden', typeSelect.value !== 'topics');
  topicLinkPanel.classList.toggle('is-hidden', typeSelect.value !== 'topics');
  const resource = activeResource();
  try {
    if (typeSelect.value === 'topics') {
      if (!currentPaths.length) await loadTopicPaths();
      currentItems = topicPathSelect.value
        ? await adminApi(`/admin/learning-paths/${Number(topicPathSelect.value)}/topics`)
        : [];
    } else {
      currentItems = await adminApi(resource.endpoint);
      if (typeSelect.value === 'lessons') currentLessons = currentItems;
    }
    renderList();
  } catch (error) { announce(error.message, true); }
}

async function renderLinkOptions() {
  if (!currentPaths.length) {
    linkTopicSelect.innerHTML = '<option value="">Create a path and topic first</option>';
    linkLessonSelect.innerHTML = '<option value="">No lesson available</option>';
    return;
  }
  if (!currentLessons.length) {
    try { currentLessons = await adminApi('/admin/lessons'); } catch (error) { announce(error.message, true); }
  }
  linkTopicSelect.innerHTML = currentItems.map((topic) => `<option value="${topic.id}">${safeText(topic.title)} · #${topic.id}</option>`).join('') || '<option value="">Create a topic first</option>';
  linkLessonSelect.innerHTML = currentLessons.map((lesson) => `<option value="${lesson.id}">${safeText(lesson.title)} · #${lesson.id}${lesson.is_published ? '' : ' (draft)'}</option>`).join('') || '<option value="">Create a lesson first</option>';
  await loadLinkedLessons();
}

async function loadLinkedLessons() {
  const topicId = Number(linkTopicSelect.value);
  const target = document.querySelector('#linked-lessons');
  if (!topicId) { target.innerHTML = '<p class="muted-label">No topic selected.</p>'; return; }
  try {
    const links = await adminApi(`/admin/learning-paths/topics/${topicId}/lessons`);
    target.innerHTML = links.length ? links.map((link) => `<div class="linked-lesson-row"><span>${safeText(link.title)} · #${link.lesson_id} · order ${link.display_order}</span><button class="button button-danger" type="button" data-unlink-lesson="${link.lesson_id}" aria-label="Unlink ${safeText(link.title)}">Unlink</button></div>`).join('') : '<p class="muted-label">No lessons linked to this topic yet.</p>';
  } catch (error) { target.innerHTML = `<p class="muted-label">${safeText(error.message)}</p>`; }
}

function fieldMarkup([name, label, kind, wide = false], item = {}) {
  const value = item[name];
  const classes = `admin-field ${wide || ['textarea', 'json'].includes(kind) ? 'wide' : ''}`;
  if (kind === 'checkbox') return `<label class="${classes}"><span>${safeText(label)}</span><input name="${name}" type="checkbox" ${value ? 'checked' : ''}></label>`;
  if (kind === 'difficulty') return `<label class="${classes}">${safeText(label)}<select name="${name}" class="admin-select">${['beginner','intermediate','advanced'].map((level) => `<option ${value === level ? 'selected' : ''}>${level}</option>`).join('')}</select></label>`;
  const inputValue = kind === 'json' ? JSON.stringify(value ?? (name === 'questions' ? [] : []), null, 2) : (value ?? (kind === 'number' ? 0 : ''));
  const required = wide ? '' : '';
  const control = ['textarea', 'json'].includes(kind)
    ? `<textarea name="${name}" class="${kind === 'json' ? 'json-field' : ''}" ${required}>${safeText(inputValue)}</textarea>`
    : `<input name="${name}" type="${kind === 'number' ? 'number' : 'text'}" ${kind === 'number' ? 'min="0"' : ''} value="${safeText(inputValue)}">`;
  return `<label class="${classes}">${safeText(label)}${control}</label>`;
}

function editItem(item = null) {
  const resource = activeResource();
  selectedId = item?.id ?? null;
  document.querySelector('#editor-title').textContent = item ? `Edit ${resource.label} #${item.id}` : `New ${resource.label}`;
  document.querySelector('#editor-empty').classList.add('is-hidden');
  formElement.classList.remove('is-hidden');
  formElement.innerHTML = resource.fields.map((field) => fieldMarkup(field, item || {})).join('') +
    `<div class="admin-form-actions"><button class="button button-primary" type="submit">${item ? 'Save changes' : 'Create item'}</button>${item && typeSelect.value !== 'topics' ? `<button class="button button-quiet" type="button" data-publish>${item.is_published ? 'Unpublish' : 'Publish'}</button><button class="button button-danger" type="button" data-delete>Delete</button>` : ''}<button class="button button-quiet" type="button" data-cancel>Cancel</button></div>`;
  renderList();
}

function readForm() {
  const data = {};
  for (const field of activeResource().fields) {
    const [name, , kind] = field;
    const control = formElement.elements.namedItem(name);
    if (kind === 'checkbox') data[name] = control.checked;
    else if (kind === 'number') data[name] = Number(control.value || 0);
    else if (kind === 'json') {
      try { data[name] = JSON.parse(control.value); }
      catch { throw new Error(`${name} must be valid JSON.`); }
    } else data[name] = control.value.trim();
  }
  return data;
}

typeSelect.addEventListener('change', loadItems);
topicPathSelect.addEventListener('change', loadItems);
document.querySelector('#new-content').addEventListener('click', () => {
  if (typeSelect.value === 'topics' && !topicPathSelect.value) {
    announce('Create a learning path before adding topics.', true);
    return;
  }
  editItem();
});
listElement.addEventListener('click', (event) => {
  const button = event.target.closest('[data-edit-id]');
  if (button) editItem(currentItems.find((item) => item.id === Number(button.dataset.editId)));
});
linkTopicSelect.addEventListener('change', loadLinkedLessons);
document.querySelector('#linked-lessons').addEventListener('click', async (event) => {
  const button = event.target.closest('[data-unlink-lesson]');
  if (!button) return;
  try {
    await adminApi(`/admin/learning-paths/topics/${Number(linkTopicSelect.value)}/lessons/${Number(button.dataset.unlinkLesson)}`, { method: 'DELETE' });
    announce('Lesson unlinked from this topic.');
    await loadLinkedLessons();
  } catch (error) { announce(error.message, true); }
});
formElement.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const resource = activeResource();
    const data = readForm();
    const url = endpointFor(resource, selectedId);
    await adminApi(url, { method: selectedId ? 'PUT' : 'POST', body: JSON.stringify(data) });
    announce(`${resource.label[0].toUpperCase()}${resource.label.slice(1)} saved.`);
    if (typeSelect.value === 'paths') await loadTopicPaths();
    await loadItems();
  } catch (error) { announce(error.message, true); }
});
formElement.addEventListener('click', async (event) => {
  if (event.target.matches('[data-cancel]')) { formElement.classList.add('is-hidden'); document.querySelector('#editor-empty').classList.remove('is-hidden'); selectedId = null; renderList(); return; }
  if (event.target.matches('[data-delete]') && selectedId !== null) {
    const item = currentItems.find((entry) => entry.id === selectedId);
    if (!window.confirm(`Delete “${item?.title || 'this item'}”? This cannot be undone.`)) return;
    try { await adminApi(endpointFor(activeResource(), selectedId), { method: 'DELETE' }); announce('Item deleted.'); await loadItems(); }
    catch (error) { announce(error.message, true); }
  }
  if (event.target.matches('[data-publish]') && selectedId !== null) {
    const item = currentItems.find((entry) => entry.id === selectedId);
    const action = item.is_published ? 'unpublish' : 'publish';
    try {
      await adminApi(`${endpointFor(activeResource(), selectedId)}/${action}`, { method: 'PATCH' });
      announce(action === 'publish' ? 'Item published.' : 'Item unpublished.');
      await loadItems();
    } catch (error) { announce(error.message, true); }
  }
});
document.querySelector('#link-lesson-button').addEventListener('click', async () => {
  const topicId = Number(linkTopicSelect.value);
  const lessonId = Number(linkLessonSelect.value);
  if (!topicId || !lessonId) return announce('Create a topic and a lesson before linking content.', true);
  try {
    await adminApi(`/admin/learning-paths/topics/${topicId}/lessons`, { method: 'PUT', body: JSON.stringify({ lesson_id: lessonId, display_order: Number(document.querySelector('#link-order').value || 0) }) });
    announce('Lesson linked to the selected topic.');
    await loadLinkedLessons();
  } catch (error) { announce(error.message, true); }
});

async function startAdminStudio() {
  const token = localStorage.getItem(ADMIN_TOKEN_KEY);
  if (!token) { deniedPanel.classList.remove('is-hidden'); return; }
  try {
    const profile = await adminApi('/auth/me');
    if (profile.role !== 'admin' || !profile.is_active) { deniedPanel.classList.remove('is-hidden'); return; }
    currentAdmin = profile;
    adminApp.classList.remove('is-hidden');
    await loadTopicPaths();
    currentLessons = await adminApi('/admin/lessons');
    await loadItems();
  } catch {
    deniedPanel.classList.remove('is-hidden');
  }
}

function switchAdminView(view) {
  const showUsers = view === 'users';
  document.querySelectorAll('[data-content-view]').forEach((element) => {
    element.classList.toggle('is-hidden', showUsers);
  });
  document.querySelector('#users-panel').classList.toggle('is-hidden', !showUsers);
  document.querySelector('#content-tab').classList.toggle('is-active', !showUsers);
  document.querySelector('#users-tab').classList.toggle('is-active', showUsers);
  if (showUsers) {
    Promise.allSettled([loadOverview(), loadUsers()]);
  } else {
    loadItems();
  }
}

async function loadOverview() {
  try {
    const overview = await adminApi('/admin/overview');
    document.querySelector('#overview-users').textContent = overview.users_total;
    document.querySelector('#overview-active').textContent = overview.users_active;
    document.querySelector('#overview-suspended').textContent = overview.users_suspended;
    document.querySelector('#overview-paths').textContent = overview.learning_paths;
    document.querySelector('#overview-lessons').textContent = overview.lessons;
    document.querySelector('#overview-quizzes').textContent = overview.quizzes;
    document.querySelector('#overview-activities').textContent = overview.practice_exercises + overview.challenges;
  } catch (error) {
    document.querySelector('#users-message').textContent = error.message;
  }
}

async function loadUsers() {
  const params = new URLSearchParams({
    limit: String(usersPageSize),
    offset: String(usersOffset),
    status_filter: document.querySelector('#user-status').value,
    role_filter: document.querySelector('#user-role').value,
  });
  const search = document.querySelector('#user-search').value.trim();
  if (search) params.set('search', search);
  try {
    const result = await adminApi(`/admin/users?${params.toString()}`);
    currentUsers = result.items;
    document.querySelector('#users-count').textContent = `${result.total} accounts`;
    document.querySelector('#users-empty').classList.toggle('is-hidden', currentUsers.length > 0);
    document.querySelector('#users-page').textContent = result.total
      ? `${usersOffset + 1}–${Math.min(usersOffset + result.items.length, result.total)} of ${result.total}` : '0 accounts';
    document.querySelector('#users-prev').disabled = usersOffset === 0;
    document.querySelector('#users-next').disabled = usersOffset + usersPageSize >= result.total;
    document.querySelector('#users-list').innerHTML = currentUsers.map((user) => `
      <article class="admin-user-row">
        <div class="user-identity"><strong>${safeText(user.name)} ${user.id === currentAdmin.id ? '<span class="user-you">YOU</span>' : ''}</strong><span>${safeText(user.email)} · #${user.id}</span></div>
        <span class="user-role-pill">${safeText(user.role)}</span>
        <span class="admin-badge ${user.is_active ? '' : 'is-draft'}">${user.is_active ? 'Active' : 'Suspended'}</span>
        <div class="user-actions">${user.id === currentAdmin.id ? '<span class="muted-label">Your account</span>' : `<button class="button button-quiet" type="button" data-user-status="${user.id}">${user.is_active ? 'Suspend' : 'Activate'}</button><button class="button button-quiet" type="button" data-user-role="${user.id}">${user.role === 'admin' ? 'Make student' : 'Make admin'}</button>`}</div>
      </article>`).join('');
  } catch (error) {
    document.querySelector('#users-message').textContent = error.message;
  }
}

document.querySelector('#content-tab').addEventListener('click', () => switchAdminView('content'));
document.querySelector('#users-tab').addEventListener('click', () => switchAdminView('users'));
document.querySelector('#user-search-button').addEventListener('click', () => { usersOffset = 0; loadUsers(); });
document.querySelector('#user-search').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') { event.preventDefault(); usersOffset = 0; loadUsers(); }
});
document.querySelector('#users-prev').addEventListener('click', () => { usersOffset = Math.max(0, usersOffset - usersPageSize); loadUsers(); });
document.querySelector('#users-next').addEventListener('click', () => { usersOffset += usersPageSize; loadUsers(); });
document.querySelector('#users-list').addEventListener('click', async (event) => {
  const statusButton = event.target.closest('[data-user-status]');
  const roleButton = event.target.closest('[data-user-role]');
  if (!statusButton && !roleButton) return;
  const userId = Number((statusButton || roleButton).dataset.userStatus || (statusButton || roleButton).dataset.userRole);
  const user = currentUsers.find((item) => item.id === userId);
  if (!user) return;
  if (statusButton) {
    const nextActive = !user.is_active;
    const operation = nextActive ? 'activate' : 'suspend';
    if (!window.confirm(`${operation[0].toUpperCase()}${operation.slice(1)} ${user.name}'s account?`)) return;
    try {
      await adminApi(`/admin/users/${userId}/status`, { method: 'PATCH', body: JSON.stringify({ is_active: nextActive }) });
      document.querySelector('#users-message').textContent = `Account ${nextActive ? 'activated' : 'suspended'}.`;
      await Promise.all([loadUsers(), loadOverview()]);
    } catch (error) { document.querySelector('#users-message').textContent = error.message; }
  } else {
    const nextRole = user.role === 'admin' ? 'student' : 'admin';
    if (!window.confirm(`Change ${user.name}'s role to ${nextRole}?`)) return;
    try {
      await adminApi(`/admin/users/${userId}/role`, { method: 'PATCH', body: JSON.stringify({ role: nextRole }) });
      document.querySelector('#users-message').textContent = `Account role changed to ${nextRole}.`;
      await loadUsers();
    } catch (error) { document.querySelector('#users-message').textContent = error.message; }
  }
});

startAdminStudio();
