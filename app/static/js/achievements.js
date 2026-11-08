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
const quizGrid = document.querySelector('#quiz-grid');
const practiceGrid = document.querySelector('#practice-grid');
const challengeGrid = document.querySelector('#challenge-grid');
const lessonDialog = document.querySelector('#lesson-dialog');
const quizDialog = document.querySelector('#quiz-dialog');
const practiceDialog = document.querySelector('#practice-dialog');
const challengeDialog = document.querySelector('#challenge-dialog');
let registerMode = false;
let currentProfile = null;
let currentLesson = null;
let currentQuiz = null;
let pendingQuizBadges = [];
let currentPractice = null;
let pendingPracticeBadges = [];
let currentChallenge = null;
let pendingChallengeBadges = [];
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
  if (!response.ok) {
    const detail = payload?.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail) ? detail.map((item) => item.msg).join(' ') : 'Request could not be completed.';
    throw new Error(message);
  }
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
  currentProfile = null;
  document.querySelector('#admin-studio-link').classList.add('is-hidden');
  dashboard.classList.add('is-hidden');
  collection.classList.add('is-hidden');
  authPanel.classList.remove('is-hidden');
  document.querySelector('#unlocked-count').textContent = '—';
});

const settingsDialog = document.querySelector('#account-settings-dialog');
const profileForm = document.querySelector('#profile-form');
const passwordForm = document.querySelector('#password-form');
const settingsMessage = document.querySelector('#settings-message');

document.querySelector('#account-settings-button').addEventListener('click', () => {
  if (!currentProfile) return;
  profileForm.elements.name.value = currentProfile.name;
  document.querySelector('#profile-email').value = currentProfile.email;
  passwordForm.reset();
  settingsMessage.textContent = '';
  settingsMessage.style.color = '#9de3b3';
  settingsDialog.showModal();
});
document.querySelector('.account-settings-close').addEventListener('click', () => settingsDialog.close());

profileForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  settingsMessage.style.color = '#ff9f9f';
  try {
    const result = await api('/auth/me', {
      method: 'PATCH',
      body: JSON.stringify({ name: profileForm.elements.name.value.trim() }),
    });
    currentProfile = result;
    document.querySelector('#welcome-title').textContent = `Welcome, ${result.name}`;
    document.querySelector('#collection-title').textContent = `${result.name}'s collection`;
    settingsMessage.style.color = '#9de3b3';
    settingsMessage.textContent = 'Display name updated.';
  } catch (error) {
    settingsMessage.textContent = error.message;
  }
});

passwordForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  settingsMessage.style.color = '#ff9f9f';
  if (passwordForm.elements.new_password.value !== passwordForm.elements.confirm_new_password.value) {
    settingsMessage.textContent = 'New password confirmation does not match.';
    return;
  }
  try {
    await api('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(Object.fromEntries(new FormData(passwordForm).entries())),
    });
    passwordForm.reset();
    settingsMessage.style.color = '#9de3b3';
    settingsMessage.textContent = 'Password changed successfully.';
  } catch (error) {
    settingsMessage.textContent = error.message;
  }
});

document.querySelector('.dialog-close').addEventListener('click', () => document.querySelector('#unlock-dialog').close());
document.querySelector('.lesson-close').addEventListener('click', () => lessonDialog.close());
document.querySelector('#complete-lesson-button').addEventListener('click', completeCurrentLesson);
document.querySelector('.quiz-close').addEventListener('click', closeQuizAndCelebrate);
document.querySelector('.practice-close').addEventListener('click', closePracticeAndCelebrate);
document.querySelector('.challenge-close').addEventListener('click', closeChallengeAndCelebrate);
quizDialog.addEventListener('cancel', (event) => {
  event.preventDefault();
  closeQuizAndCelebrate();
});

quizGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-quiz-id]');
  if (!button) return;
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Loading…';
  try {
    currentQuiz = await api(`/quizzes/${button.dataset.quizId}`);
    showQuiz(currentQuiz);
  } catch (error) {
    pageMessage.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
});

quizDialog.addEventListener('submit', submitCurrentQuiz);
quizDialog.addEventListener('click', (event) => {
  if (event.target.closest('.quiz-done')) closeQuizAndCelebrate();
});

practiceGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-exercise-id]');
  if (!button) return;
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Loading…';
  try {
    currentPractice = await api(`/practice/${button.dataset.exerciseId}`);
    showPractice(currentPractice);
  } catch (error) {
    pageMessage.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
});

practiceDialog.addEventListener('submit', submitPracticeAnswer);
practiceDialog.addEventListener('click', (event) => {
  if (event.target.closest('.practice-done')) closePracticeAndCelebrate();
});
practiceDialog.addEventListener('cancel', (event) => {
  event.preventDefault();
  closePracticeAndCelebrate();
});

challengeGrid.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-challenge-id]');
  if (!button) return;
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = 'Loading…';
  try {
    currentChallenge = await api(`/challenges/${button.dataset.challengeId}`);
    showChallenge(currentChallenge);
  } catch (error) {
    pageMessage.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
});

challengeDialog.addEventListener('submit', submitChallengeAnswer);
challengeDialog.addEventListener('click', (event) => {
  const hintButton = event.target.closest('[data-hint-index]');
  if (hintButton && currentChallenge) {
    const hint = currentChallenge.hints[Number(hintButton.dataset.hintIndex)];
    hintButton.parentElement.textContent = `Hint: ${hint}`;
    return;
  }
  if (event.target.closest('.challenge-done')) closeChallengeAndCelebrate();
});
challengeDialog.addEventListener('cancel', (event) => {
  event.preventDefault();
  closeChallengeAndCelebrate();
});

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

function renderQuizzes(quizzes, history) {
  const attemptsByQuiz = new Map();
  history.forEach((attempt) => {
    if (!attemptsByQuiz.has(attempt.quiz_id)) attemptsByQuiz.set(attempt.quiz_id, attempt);
  });
  document.querySelector('#quiz-count').textContent = `${quizzes.length} ${quizzes.length === 1 ? 'quiz' : 'quizzes'}`;
  document.querySelector('#quiz-empty').classList.toggle('is-hidden', quizzes.length > 0);
  quizGrid.innerHTML = quizzes.map((quiz) => {
    const attempt = attemptsByQuiz.get(quiz.id);
    return `<article class="quiz-card">
      <div class="quiz-card-top"><span class="difficulty-pill">${escapeHTML(quiz.difficulty)}</span><span class="question-count">${quiz.question_count} questions</span></div>
      <h3>${escapeHTML(quiz.title)}</h3>
      <p>${escapeHTML(quiz.description || 'Review Linux concepts and check your understanding.')}</p>
      ${attempt ? `<p class="path-meta">Latest: ${attempt.percentage}% · ${attempt.score}/${attempt.total_questions}</p>` : ''}
      <button class="button button-primary" type="button" data-quiz-id="${quiz.id}">${attempt ? 'Retake quiz' : 'Start quiz'}</button>
    </article>`;
  }).join('');

  const historySection = document.querySelector('#quiz-history');
  const historyList = document.querySelector('#quiz-history-list');
  historySection.classList.toggle('is-hidden', history.length === 0);
  historyList.innerHTML = history.slice(0, 5).map((attempt) => {
    const quiz = quizzes.find((item) => item.id === attempt.quiz_id);
    return `<div class="history-row"><span>${escapeHTML(quiz?.title || 'Quiz')}</span><span>${attempt.score}/${attempt.total_questions} · <strong>${attempt.percentage}%</strong></span></div>`;
  }).join('');
}

function renderPractice(exercises, history) {
  const attemptsByExercise = new Map();
  history.forEach((attempt) => {
    if (!attemptsByExercise.has(attempt.exercise_id)) attemptsByExercise.set(attempt.exercise_id, []);
    attemptsByExercise.get(attempt.exercise_id).push(attempt);
  });
  document.querySelector('#practice-count').textContent = `${exercises.length} ${exercises.length === 1 ? 'exercise' : 'exercises'}`;
  document.querySelector('#practice-empty').classList.toggle('is-hidden', exercises.length > 0);
  practiceGrid.innerHTML = exercises.map((exercise) => {
    const attempts = attemptsByExercise.get(exercise.id) || [];
    const latest = attempts[0];
    return `<article class="practice-card">
      <div class="practice-card-top"><span class="difficulty-pill">${escapeHTML(exercise.difficulty)}</span><span class="question-count">${attempts.length} ${attempts.length === 1 ? 'attempt' : 'attempts'}</span></div>
      <h3>${escapeHTML(exercise.title)}</h3>
      <p>${escapeHTML(exercise.description || 'Practice a Linux command and check your answer.')}</p>
      ${latest ? `<p class="path-meta">Latest: ${latest.is_correct ? 'Correct ✓' : 'Try again'}</p>` : ''}
      <button class="button button-primary" type="button" data-exercise-id="${exercise.id}">${latest?.is_correct ? 'Practice again' : 'Open exercise'}</button>
    </article>`;
  }).join('');

  const historySection = document.querySelector('#practice-history');
  const historyList = document.querySelector('#practice-history-list');
  historySection.classList.toggle('is-hidden', history.length === 0);
  historyList.innerHTML = history.slice(0, 5).map((attempt) => {
    const exercise = exercises.find((item) => item.id === attempt.exercise_id);
    return `<div class="history-row"><span>${escapeHTML(exercise?.title || 'Practice exercise')}</span><span><strong>${attempt.is_correct ? 'Correct' : 'Try again'}</strong></span></div>`;
  }).join('');
}

function renderChallenges(challenges, history) {
  const attemptsByChallenge = new Map();
  history.forEach((attempt) => {
    if (!attemptsByChallenge.has(attempt.challenge_id)) attemptsByChallenge.set(attempt.challenge_id, []);
    attemptsByChallenge.get(attempt.challenge_id).push(attempt);
  });
  document.querySelector('#challenge-count').textContent = `${challenges.length} ${challenges.length === 1 ? 'challenge' : 'challenges'}`;
  document.querySelector('#challenge-empty').classList.toggle('is-hidden', challenges.length > 0);
  challengeGrid.innerHTML = challenges.map((challenge) => {
    const attempts = attemptsByChallenge.get(challenge.id) || [];
    const latest = attempts[0];
    return `<article class="challenge-card">
      <div class="challenge-card-top"><span class="difficulty-pill">${escapeHTML(challenge.difficulty)}</span><span class="question-count">${attempts.length} ${attempts.length === 1 ? 'attempt' : 'attempts'}</span></div>
      <h3>${escapeHTML(challenge.title)}</h3>
      <p>${escapeHTML(challenge.description || 'Solve a Linux scenario using the command line.')}</p>
      ${latest ? `<p class="path-meta">Latest: ${latest.is_correct ? 'Solved ✓' : 'Try again'}</p>` : ''}
      <button class="button button-primary" type="button" data-challenge-id="${challenge.id}">${latest?.is_correct ? 'Review challenge' : 'Solve challenge'}</button>
    </article>`;
  }).join('');

  const historySection = document.querySelector('#challenge-history');
  const historyList = document.querySelector('#challenge-history-list');
  historySection.classList.toggle('is-hidden', history.length === 0);
  historyList.innerHTML = history.slice(0, 5).map((attempt) => {
    const challenge = challenges.find((item) => item.id === attempt.challenge_id);
    return `<div class="history-row"><span>${escapeHTML(challenge?.title || 'Challenge')}</span><span><strong>${attempt.is_correct ? 'Solved' : 'Try again'}</strong></span></div>`;
  }).join('');
}

function showChallenge(challenge) {
  document.querySelector('#challenge-message').textContent = '';
  document.querySelector('#challenge-content').innerHTML = `
    <p class="eyebrow">${escapeHTML(challenge.difficulty)} CHALLENGE</p>
    <h2>${escapeHTML(challenge.title)}</h2>
    ${challenge.description ? `<p>${escapeHTML(challenge.description)}</p>` : ''}
    <div class="challenge-scenario">${escapeHTML(challenge.scenario)}</div>
    <p class="challenge-instructions">${escapeHTML(challenge.instructions)}</p>
    ${challenge.hints?.length ? `<div class="hint-list"><p class="eyebrow">NEED A HINT?</p>${challenge.hints.map((hint, index) => `<div class="hint-row"><button type="button" data-hint-index="${index}">Reveal hint ${index + 1}</button></div>`).join('')}</div>` : ''}
    <form id="challenge-form" data-challenge-id="${challenge.id}">
      <label class="challenge-answer-label" for="challenge-answer">Your Linux command
        <input id="challenge-answer" class="challenge-answer" name="answer" type="text" maxlength="2000" autocomplete="off" spellcheck="false" required>
      </label>
      <button class="button button-primary" type="submit">Check solution</button>
    </form>`;
  challengeDialog.showModal();
  document.querySelector('#challenge-answer').focus();
}

async function submitChallengeAnswer(event) {
  if (event.target.id !== 'challenge-form') return;
  event.preventDefault();
  if (!currentChallenge || !event.target.reportValidity()) return;
  const form = event.target;
  const submitButton = form.querySelector('[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Checking solution…';
  const answer = new FormData(form).get('answer');
  try {
    const result = await api(`/challenges/${currentChallenge.id}/attempts`, {
      method: 'POST', body: JSON.stringify({ answer }),
    });
    if (!result.is_correct) {
      const message = document.querySelector('#challenge-message');
      message.style.color = '#ffb6a3';
      message.textContent = result.feedback;
      form.reset();
      submitButton.disabled = false;
      submitButton.textContent = 'Try again';
      await loadDashboard(false);
      document.querySelector('#challenge-answer')?.focus();
      return;
    }

    pendingChallengeBadges = result.newly_unlocked || [];
    const badgeMessage = pendingChallengeBadges.length
      ? `<p class="result-badges">New badge${pendingChallengeBadges.length > 1 ? 's' : ''}: ${pendingChallengeBadges.map((badge) => escapeHTML(badge.title)).join(', ')}</p>`
      : '';
    document.querySelector('#challenge-content').innerHTML = `
      <div class="challenge-result">
        <p class="eyebrow">CHALLENGE SOLVED</p>
        <h2>Well done!</h2>
        <p>${escapeHTML(result.feedback)}</p>
        <p class="result-xp">${result.xp_awarded > 0 ? `+${result.xp_awarded} XP` : `${result.total_xp} total XP`}</p>
        <p>Level ${result.level} · ${result.challenges_completed} challenges completed</p>
        ${badgeMessage}
        <button class="button button-primary challenge-done" type="button">Continue</button>
      </div>`;
    await loadDashboard(false);
  } catch (error) {
    document.querySelector('#challenge-message').textContent = error.message;
    submitButton.disabled = false;
    submitButton.textContent = 'Check solution';
  }
}

function closeChallengeAndCelebrate() {
  if (challengeDialog.open) challengeDialog.close();
  if (pendingChallengeBadges.length) {
    const unlocked = pendingChallengeBadges;
    pendingChallengeBadges = [];
    window.setTimeout(() => celebrateBadges(unlocked), 150);
  }
}

function showQuiz(quiz) {
  document.querySelector('#quiz-message').textContent = '';
  document.querySelector('#quiz-content').innerHTML = `
    <p class="eyebrow">${escapeHTML(quiz.difficulty)} QUIZ</p>
    <h2>${escapeHTML(quiz.title)}</h2>
    ${quiz.description ? `<p class="quiz-intro">${escapeHTML(quiz.description)}</p>` : ''}
    <p class="quiz-pass-note">Choose one answer for each question. Pass mark: 60%.</p>
    <form id="quiz-form" data-quiz-id="${quiz.id}">
      ${quiz.questions.map((question, index) => `
        <fieldset class="quiz-question">
          <legend>${index + 1}. ${escapeHTML(question.prompt)}</legend>
          ${question.options.map((option, optionIndex) => `
            <label class="quiz-option"><input type="radio" name="question-${question.id}" value="${optionIndex}" required><span>${escapeHTML(option)}</span></label>`).join('')}
        </fieldset>`).join('')}
      <button class="button button-primary quiz-submit" type="submit">Submit answers</button>
    </form>`;
  quizDialog.showModal();
}

function showPractice(exercise) {
  document.querySelector('#practice-message').textContent = '';
  document.querySelector('#practice-content').innerHTML = `
    <p class="eyebrow">${escapeHTML(exercise.difficulty)} PRACTICE</p>
    <h2>${escapeHTML(exercise.title)}</h2>
    ${exercise.description ? `<p>${escapeHTML(exercise.description)}</p>` : ''}
    <div class="practice-instructions">${escapeHTML(exercise.instructions)}</div>
    <form id="practice-form" data-exercise-id="${exercise.id}">
      <label class="practice-answer-label" for="practice-answer">Your answer
        <input id="practice-answer" class="practice-answer" name="answer" type="text" maxlength="2000" autocomplete="off" spellcheck="false" required>
      </label>
      <button class="button button-primary" type="submit">Check answer</button>
    </form>`;
  practiceDialog.showModal();
  document.querySelector('#practice-answer').focus();
}

async function submitPracticeAnswer(event) {
  if (event.target.id !== 'practice-form') return;
  event.preventDefault();
  if (!currentPractice || !event.target.reportValidity()) return;
  const form = event.target;
  const submitButton = form.querySelector('[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Checking answer…';
  const answer = new FormData(form).get('answer');
  try {
    const result = await api(`/practice/${currentPractice.id}/attempts`, {
      method: 'POST', body: JSON.stringify({ answer }),
    });
    pendingPracticeBadges = result.newly_unlocked || [];
    const resultClass = result.is_correct ? 'practice-result' : 'practice-result is-incorrect';
    const badgeMessage = pendingPracticeBadges.length
      ? `<p class="result-badges">New badge${pendingPracticeBadges.length > 1 ? 's' : ''}: ${pendingPracticeBadges.map((badge) => escapeHTML(badge.title)).join(', ')}</p>`
      : '';
    document.querySelector('#practice-content').innerHTML = `
      <div class="${resultClass}">
        <p class="eyebrow">${result.is_correct ? 'CORRECT ANSWER' : 'ANSWER RECORDED'}</p>
        <h2>${result.is_correct ? 'Nice work!' : 'Keep trying'}</h2>
        <p>${escapeHTML(result.feedback)}</p>
        <p class="result-xp">${result.xp_awarded > 0 ? `+${result.xp_awarded} XP` : `${result.total_xp} total XP`}</p>
        <p>Level ${result.level} · ${result.practice_completed} exercises completed</p>
        ${badgeMessage}
        <button class="button button-primary practice-done" type="button">Continue</button>
      </div>`;
    await loadDashboard(false);
  } catch (error) {
    document.querySelector('#practice-message').textContent = error.message;
    submitButton.disabled = false;
    submitButton.textContent = 'Check answer';
  }
}

function closePracticeAndCelebrate() {
  if (practiceDialog.open) practiceDialog.close();
  if (pendingPracticeBadges.length) {
    const unlocked = pendingPracticeBadges;
    pendingPracticeBadges = [];
    window.setTimeout(() => celebrateBadges(unlocked), 150);
  }
}

async function submitCurrentQuiz(event) {
  if (event.target.id !== 'quiz-form') return;
  event.preventDefault();
  if (!currentQuiz || !event.target.reportValidity()) return;
  const form = event.target;
  const submitButton = form.querySelector('[type="submit"]');
  submitButton.disabled = true;
  submitButton.textContent = 'Checking answers…';
  const answers = currentQuiz.questions.map((question) => {
    const selected = form.querySelector(`input[name="question-${question.id}"]:checked`);
    return { question_id: question.id, selected_option_index: Number(selected.value) };
  });
  try {
    const result = await api(`/quizzes/${currentQuiz.id}/attempts`, {
      method: 'POST', body: JSON.stringify({ answers }),
    });
    pendingQuizBadges = result.newly_unlocked || [];
    const resultClass = result.passed ? 'quiz-result' : 'quiz-result is-failed';
    const badgeMessage = pendingQuizBadges.length
      ? `<p class="result-badges">New badge${pendingQuizBadges.length > 1 ? 's' : ''}: ${pendingQuizBadges.map((badge) => escapeHTML(badge.title)).join(', ')}</p>`
      : '';
    document.querySelector('#quiz-content').innerHTML = `
      <div class="${resultClass}">
        <p class="eyebrow">${result.passed ? 'QUIZ PASSED' : 'QUIZ COMPLETE'}</p>
        <h2>${result.passed ? 'Great work!' : 'Keep practicing'}</h2>
        <span class="score">${result.percentage}%</span>
        <p>${result.score} of ${result.total_questions} correct</p>
        <p>${result.xp_awarded > 0 ? `+${result.xp_awarded} XP earned` : 'XP for this quiz was already collected'}</p>
        <p>Total XP: ${result.total_xp} · Level ${result.level}</p>
        ${badgeMessage}
        <button class="button button-primary quiz-done" type="button">Continue</button>
      </div>`;
    await loadDashboard(false);
  } catch (error) {
    document.querySelector('#quiz-message').textContent = error.message;
    submitButton.disabled = false;
    submitButton.textContent = 'Submit answers';
  }
}

function closeQuizAndCelebrate() {
  if (quizDialog.open) quizDialog.close();
  if (pendingQuizBadges.length) {
    const unlocked = pendingQuizBadges;
    pendingQuizBadges = [];
    window.setTimeout(() => celebrateBadges(unlocked), 150);
  }
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

function renderGamification(streak, leaderboard) {
  document.querySelector('#stat-streak').textContent = `${streak.current_streak} ${streak.current_streak === 1 ? 'day' : 'days'}`;
  document.querySelector('#streak-best').textContent = `Best: ${streak.longest_streak} days · ${streak.active_days_this_week}/7 this week`;
  const list = document.querySelector('#leaderboard-list');
  const entries = leaderboard.entries || [];
  document.querySelector('#leaderboard-empty').classList.toggle('is-hidden', entries.length > 0);
  list.innerHTML = entries.map((entry) => `
    <article class="leaderboard-row ${entry.is_current_user ? 'is-you' : ''}">
      <span class="leaderboard-place">#${entry.rank}</span>
      <span class="leaderboard-name">${escapeHTML(entry.name)}${entry.is_current_user ? ' <b>(you)</b>' : ''}</span>
      <span class="leaderboard-level">Level ${entry.level}</span>
      <strong class="leaderboard-xp">${entry.total_xp} XP</strong>
    </article>`).join('');
  document.querySelector('#leaderboard-rank').textContent = leaderboard.current_user_rank
    ? `Your rank: #${leaderboard.current_user_rank}` : 'Your rank will appear after earning XP';
}

async function loadDashboard(celebrateNew = false) {
  pageMessage.textContent = '';
  try {
    const [profile, summary, paths, completions, badges, quizzes, quizHistory, exercises, practiceHistory, challenges, challengeHistory] = await Promise.all([
      api('/auth/me'), api('/dashboard'), api('/learning-paths'),
      api('/lessons/completed/me'), api('/achievements/me'), api('/quizzes'),
      api('/quizzes/attempts/me'), api('/practice'), api('/practice/attempts/me'),
      api('/challenges'), api('/challenges/attempts/me'),
    ]);
    currentProfile = profile;
    authPanel.classList.add('is-hidden');
    dashboard.classList.remove('is-hidden');
    collection.classList.remove('is-hidden');
    document.querySelector('#admin-studio-link').classList.toggle('is-hidden', profile.role !== 'admin' || !profile.is_active);
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
    renderQuizzes(quizzes, quizHistory);
    renderPractice(exercises, practiceHistory);
    renderChallenges(challenges, challengeHistory);
    renderBadges(badges.achievements);
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    const utcOffsetMinutes = new Date().getTimezoneOffset();
    const gamification = await Promise.allSettled([
      api(`/gamification/streak?timezone=${encodeURIComponent(timezone)}&utc_offset_minutes=${utcOffsetMinutes}`),
      api('/gamification/leaderboard?limit=10'),
    ]);
    if (gamification.every((result) => result.status === 'fulfilled')) {
      renderGamification(gamification[0].value, gamification[1].value);
    } else {
      document.querySelector('#stat-streak').textContent = '—';
      document.querySelector('#streak-best').textContent = 'Streak unavailable';
      document.querySelector('#leaderboard-rank').textContent = 'Leaderboard unavailable';
    }
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
    document.querySelector('#admin-studio-link').classList.add('is-hidden');
    authPanel.classList.remove('is-hidden');
    authMessage.textContent = error.message;
  }
}

if (localStorage.getItem(TOKEN_KEY)) loadDashboard(true);
