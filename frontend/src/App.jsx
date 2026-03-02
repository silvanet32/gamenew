import { useMemo, useState } from 'react'
import { GlassCard } from './react-bites/GlassCard'
import { NeonButton } from './react-bites/NeonButton'
import { StatusPill } from './react-bites/StatusPill'

const mockSeries = [
  { id: 1, title: 'Dark', description: 'Mistério com viagem no tempo.', views: 2345 },
  { id: 2, title: 'Arcane', description: 'Animação épica no universo de LoL.', views: 1984 }
]

const mockDonations = [
  { id: 1, name: 'PIX', key: 'contato@gamenew.com', active: true },
  { id: 2, name: 'PayPal', key: 'paypal.me/gamenew', active: false }
]

export default function App() {
  const [series, setSeries] = useState(mockSeries)
  const [donations, setDonations] = useState(mockDonations)
  const [form, setForm] = useState({ title: '', description: '' })

  const totalViews = useMemo(() => series.reduce((acc, item) => acc + item.views, 0), [series])

  function addSerie(e) {
    e.preventDefault()
    if (!form.title.trim()) return
    setSeries((prev) => [
      { id: Date.now(), title: form.title, description: form.description, views: 0 },
      ...prev
    ])
    setForm({ title: '', description: '' })
  }

  function removeSerie(id) {
    setSeries((prev) => prev.filter((item) => item.id !== id))
  }

  function toggleDonation(id) {
    setDonations((prev) =>
      prev.map((item) => (item.id === id ? { ...item, active: !item.active } : item))
    )
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="tag">React + Vite + React-bites UI</p>
        <h1>GameNew Dashboard</h1>
        <p>Interface moderna para login, administração de séries e gestão de doações.</p>
      </header>

      <main className="grid">
        <GlassCard title="Autenticação">
          <div className="auth-grid">
            <input placeholder="E-mail" defaultValue="admin@gmail.com" />
            <input placeholder="Senha" type="password" defaultValue="admin123" />
            <NeonButton>Entrar</NeonButton>
          </div>
        </GlassCard>

        <GlassCard title="Resumo admin">
          <div className="stats">
            <div><strong>{series.length}</strong><span>Séries</span></div>
            <div><strong>{totalViews}</strong><span>Views</span></div>
            <div><strong>{donations.filter((d) => d.active).length}</strong><span>Doações ativas</span></div>
          </div>
        </GlassCard>

        <GlassCard title="Adicionar / editar série">
          <form className="form" onSubmit={addSerie}>
            <input
              placeholder="Título da série"
              value={form.title}
              onChange={(e) => setForm((old) => ({ ...old, title: e.target.value }))}
            />
            <textarea
              placeholder="Descrição"
              value={form.description}
              onChange={(e) => setForm((old) => ({ ...old, description: e.target.value }))}
            />
            <NeonButton type="submit">Salvar série</NeonButton>
          </form>
        </GlassCard>

        <GlassCard title="Séries cadastradas">
          <div className="list">
            {series.map((item) => (
              <article key={item.id} className="list-item">
                <div>
                  <h4>{item.title}</h4>
                  <p>{item.description || 'Sem descrição'}</p>
                  <small>{item.views} views</small>
                </div>
                <NeonButton variant="danger" onClick={() => removeSerie(item.id)}>Excluir</NeonButton>
              </article>
            ))}
          </div>
        </GlassCard>

        <GlassCard title="Métodos de doação">
          <div className="list">
            {donations.map((item) => (
              <article key={item.id} className="list-item">
                <div>
                  <h4>{item.name}</h4>
                  <p>{item.key}</p>
                </div>
                <div className="rb-actions">
                  <StatusPill active={item.active} />
                  <NeonButton variant="secondary" onClick={() => toggleDonation(item.id)}>
                    Alternar
                  </NeonButton>
                </div>
              </article>
            ))}
          </div>
        </GlassCard>
      </main>
    </div>
  )
}
