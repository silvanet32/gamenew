export function StatusPill({ active }) {
  return <span className={`rb-pill ${active ? 'rb-pill--active' : 'rb-pill--inactive'}`}>{active ? 'Ativo' : 'Inativo'}</span>
}
