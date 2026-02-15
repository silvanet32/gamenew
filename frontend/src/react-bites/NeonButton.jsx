export function NeonButton({ children, variant = 'primary', ...props }) {
  return (
    <button className={`rb-neon-btn rb-neon-btn--${variant}`} {...props}>
      {children}
    </button>
  )
}
