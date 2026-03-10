export default function Loading({ inline }) {
  if (inline) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 20, height: 20, position: 'relative', flexShrink: 0 }}>
          <div className="anim-spin" style={{
            position: 'absolute', inset: 0, borderRadius: '50%',
            border: '2px solid transparent', borderTopColor: '#3b82f6',
          }} />
        </div>
        <span style={{ color: '#64748b', fontFamily: '"Space Mono",monospace', fontSize: 12 }}>Thinking…</span>
      </div>
    )
  }
  return (
    <div style={{ textAlign: 'center', padding: '70px 0' }}>
      <div style={{ width: 56, height: 56, position: 'relative', margin: '0 auto 16px' }}>
        <div className="anim-spin" style={{
          position: 'absolute', inset: 0, borderRadius: '50%',
          border: '2px solid transparent', borderTopColor: '#3b82f6',
        }} />
        <div className="anim-spin-r" style={{
          position: 'absolute', inset: 8, borderRadius: '50%',
          border: '2px solid transparent', borderBottomColor: '#8b5cf6',
        }} />
      </div>
      <p style={{ color: '#64748b', fontFamily: '"Space Mono",monospace', fontSize: 13 }}>
        Analyzing data…
      </p>
    </div>
  )
}
