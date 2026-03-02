export function GlassCard({ title, children, actions }) {
  return (
    <section className="rb-glass-card">
      <header className="rb-glass-card__header">
        <h3>{title}</h3>
        {actions ? <div className="rb-actions">{actions}</div> : null}
      </header>
      <div className="rb-glass-card__content">{children}</div>
    </section>
  )
}
