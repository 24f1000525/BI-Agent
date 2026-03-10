export default function HistoryPanel({ history, onSelect }) {
  if (!history || history.length === 0) return null

  const userMsgs = history.filter(m => m.role === 'user')

  return (
    <div style={{
      background: 'linear-gradient(135deg,#0a1628ee,#0d1f3ccc)',
      border: '1px solid #1a3a6b', borderRadius: 14, padding: '16px',
      marginBottom: 24,
    }}>
      <div style={{
        fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
        textTransform: 'uppercase', color: '#64748b', marginBottom: 12,
      }}>◈ Query History</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {userMsgs.map((msg, i) => (
          <button
            key={i}
            onClick={() => onSelect?.(msg.content)}
            style={{
              background: 'rgba(59,130,246,0.06)', border: '1px solid #1a3a6b',
              borderRadius: 8, padding: '8px 14px', fontSize: 11, color: '#64748b',
              cursor: 'pointer', textAlign: 'left',
              transition: 'all .15s',
            }}
            onMouseOver={e => { e.currentTarget.style.borderColor = '#3b82f6'; e.currentTarget.style.color = '#93c5fd' }}
            onMouseOut={e => { e.currentTarget.style.borderColor = '#1a3a6b'; e.currentTarget.style.color = '#64748b' }}
          >
            <span style={{ marginRight: 6, opacity: 0.5 }}>#{i + 1}</span>
            {msg.content.length > 80 ? msg.content.slice(0, 80) + '…' : msg.content}
          </button>
        ))}
      </div>
    </div>
  )
}
