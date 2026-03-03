function showAuthTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  document.querySelectorAll('.auth-tab').forEach((t, i) => {
    t.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'register'));
  });
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('login-error');
  errorEl.classList.add('hidden');

  try {
    const data = await api.login(email, password);
    if (!data) return;
    setToken(data.access_token);
    setUser(data.user);
    initApp();
  } catch (err) {
    errorEl.textContent = err.detail || 'Login failed';
    errorEl.classList.remove('hidden');
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById('reg-name').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const errorEl = document.getElementById('register-error');
  errorEl.classList.add('hidden');

  try {
    const data = await api.register(name, email, password);
    if (!data) return;
    setToken(data.access_token);
    setUser(data.user);
    initApp();
  } catch (err) {
    errorEl.textContent = err.detail || 'Registration failed';
    errorEl.classList.remove('hidden');
  }
}

function handleLogout() {
  clearToken();
  showAuthScreen();
}