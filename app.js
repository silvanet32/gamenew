const storageKeys = {
  users: 'gamenew_users',
  session: 'gamenew_session',
  series: 'gamenew_series',
  donation: 'gamenew_donation'
};

function load(key, fallback) {
  const raw = localStorage.getItem(key);
  return raw ? JSON.parse(raw) : fallback;
}

function save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function bootstrap() {
  const users = load(storageKeys.users, []);
  if (!users.find((u) => u.email === 'admin@gamenew.com')) {
    users.push({ id: Date.now(), name: 'Administrador', email: 'admin@gamenew.com', password: 'admin123', isAdmin: true });
    save(storageKeys.users, users);
  }

  if (!localStorage.getItem(storageKeys.donation)) {
    save(storageKeys.donation, {
      method: 'PIX',
      key: 'sua-chave-pix-aqui',
      message: 'Sua doação ajuda a manter novas séries no ar ❤️'
    });
  }

  if (!localStorage.getItem(storageKeys.series)) {
    save(storageKeys.series, []);
  }
}

function getCurrentUser() {
  return load(storageKeys.session, null);
}

function setCurrentUser(user) {
  save(storageKeys.session, user);
}

function renderDonation() {
  const donation = load(storageKeys.donation, { method: '', key: '', message: '' });
  document.getElementById('donationMethod').textContent = donation.method;
  document.getElementById('donationKey').textContent = donation.key;
  document.getElementById('donationMessage').textContent = donation.message;

  const donationForm = document.getElementById('donationForm');
  donationForm.method.value = donation.method;
  donationForm.key.value = donation.key;
  donationForm.message.value = donation.message;
}

function renderSeries() {
  const series = load(storageKeys.series, []);
  const currentUser = getCurrentUser();
  const list = document.getElementById('seriesList');
  list.innerHTML = '';

  if (series.length === 0) {
    list.innerHTML = '<p class="muted">Nenhuma série publicada ainda.</p>';
    return;
  }

  series.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'series-card';
    card.innerHTML = `
      ${item.cover ? `<img src="${item.cover}" alt="Capa ${item.title}" />` : ''}
      <h3>${item.title}</h3>
      <p>${item.description}</p>
      ${currentUser?.isAdmin ? `
        <div class="actions">
          <button data-edit="${item.id}">Editar</button>
          <button class="danger" data-delete="${item.id}">Excluir</button>
        </div>
      ` : ''}
    `;
    list.appendChild(card);
  });

  list.querySelectorAll('[data-edit]').forEach((btn) => {
    btn.addEventListener('click', () => startEditSeries(Number(btn.dataset.edit)));
  });

  list.querySelectorAll('[data-delete]').forEach((btn) => {
    btn.addEventListener('click', () => deleteSeries(Number(btn.dataset.delete)));
  });
}

function startEditSeries(id) {
  const series = load(storageKeys.series, []);
  const item = series.find((s) => s.id === id);
  if (!item) return;
  const form = document.getElementById('seriesForm');
  form.title.value = item.title;
  form.description.value = item.description;
  form.cover.value = item.cover || '';
  form.editId.value = item.id;
  document.getElementById('seriesFormTitle').textContent = `Editando: ${item.title}`;
}

function deleteSeries(id) {
  if (!confirm('Deseja excluir esta série?')) return;
  const series = load(storageKeys.series, []).filter((item) => item.id !== id);
  save(storageKeys.series, series);
  renderSeries();
}

function updateUIByAuth() {
  const user = getCurrentUser();
  document.getElementById('userStatus').textContent = user ? `${user.name}${user.isAdmin ? ' (Admin)' : ''}` : 'Visitante';
  document.getElementById('logoutBtn').classList.toggle('hidden', !user);
  document.getElementById('authSection').classList.toggle('hidden', Boolean(user));
  document.getElementById('adminSection').classList.toggle('hidden', !(user && user.isAdmin));
}

function setupEvents() {
  document.getElementById('registerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    const users = load(storageKeys.users, []);

    if (users.find((u) => u.email === data.email)) {
      alert('E-mail já cadastrado.');
      return;
    }

    users.push({ id: Date.now(), name: data.name, email: data.email, password: data.password, isAdmin: false });
    save(storageKeys.users, users);
    alert('Conta criada com sucesso! Agora faça login.');
    e.target.reset();
  });

  document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    const users = load(storageKeys.users, []);
    const user = users.find((u) => u.email === data.email && u.password === data.password);

    if (!user) {
      alert('Credenciais inválidas.');
      return;
    }

    setCurrentUser({ id: user.id, name: user.name, email: user.email, isAdmin: user.isAdmin });
    updateUIByAuth();
    renderSeries();
  });

  document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem(storageKeys.session);
    updateUIByAuth();
    renderSeries();
  });

  document.getElementById('seriesForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const currentUser = getCurrentUser();
    if (!currentUser?.isAdmin) return;

    const form = Object.fromEntries(new FormData(e.target));
    const series = load(storageKeys.series, []);

    if (form.editId) {
      const idx = series.findIndex((s) => s.id === Number(form.editId));
      if (idx !== -1) {
        series[idx] = { ...series[idx], title: form.title, description: form.description, cover: form.cover };
      }
    } else {
      series.unshift({ id: Date.now(), title: form.title, description: form.description, cover: form.cover });
    }

    save(storageKeys.series, series);
    e.target.reset();
    e.target.editId.value = '';
    document.getElementById('seriesFormTitle').textContent = 'Nova série';
    renderSeries();
  });

  document.getElementById('donationForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const currentUser = getCurrentUser();
    if (!currentUser?.isAdmin) return;

    const form = Object.fromEntries(new FormData(e.target));
    save(storageKeys.donation, { method: form.method, key: form.key, message: form.message });
    renderDonation();
    alert('Configuração de doação atualizada.');
  });
}

bootstrap();
setupEvents();
updateUIByAuth();
renderDonation();
renderSeries();
