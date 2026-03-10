export default function Header({ schema, onUpload, onClear }) {
  return (
    <header style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '16px 28px',
      background: 'linear-gradient(90deg,#0a1628f2,#0d1f3cf2)',
      borderBottom: '1px solid #1a3a6b55',
      backdropFilter: 'blur(20px)',
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16,
        }}>⬡</div>
        <div>
          <div style={{
            fontSize: 17, fontWeight: 800, letterSpacing: '-0.3px',
            background: 'linear-gradient(90deg,#3b82f6,#8b5cf6)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>DataLens AI</div>
          <div style={{ fontSize: 10, color: '#475569', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Conversational Analytics
          </div>
        </div>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {schema && (
          <div style={{
            background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.25)',
            borderRadius: 8, padding: '5px 12px', display: 'flex', alignItems: 'center', gap: 7,
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399' }} />
            <span style={{ fontSize: 12, color: '#6ee7b7', fontWeight: 500 }}>{schema.name}</span>
            <span style={{ fontSize: 11, color: '#475569' }}>{schema.rows?.toLocaleString()} rows</span>
            <button
              onClick={onClear}
              style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: 15, padding: 0 }}
              onMouseOver={e => e.currentTarget.style.color = '#f87171'}
              onMouseOut={e => e.currentTarget.style.color = '#475569'}
            >×</button>
          </div>
        )}
        <label style={{
          background: 'linear-gradient(135deg,#3b82f6,#2563eb)', borderRadius: 8,
          padding: '7px 16px', fontSize: 12, color: '#fff', cursor: 'pointer', fontWeight: 600,
        }}>
          ⬆ Upload CSV
          <input type="file" accept=".csv" style={{ display: 'none' }} onChange={onUpload} />
        </label>
      </div>
    </header>
  )
}
