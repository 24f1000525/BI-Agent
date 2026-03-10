export default function Sidebar({ schema, onUpload, onClear }) {
  return (
    <aside style={{
      width: 260, flexShrink: 0,
      background: 'linear-gradient(180deg,#0a1628f5,#0d1f3cf5)',
      borderRight: '1px solid #1a3a6b55',
      backdropFilter: 'blur(20px)',
      display: 'flex', flexDirection: 'column',
      padding: '24px 16px', gap: 16,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 9,
          background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14,
        }}>⬡</div>
        <span style={{
          fontSize: 15, fontWeight: 800,
          background: 'linear-gradient(90deg,#3b82f6,#8b5cf6)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>DataLens AI</span>
      </div>

      {/* Upload zone */}
      <label style={{
        border: '2px dashed #1a3a6b', borderRadius: 12, padding: '20px 12px',
        textAlign: 'center', cursor: 'pointer',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
        transition: 'border-color .2s, background .2s',
        background: 'rgba(59,130,246,0.04)',
      }}
        onMouseOver={e => e.currentTarget.style.borderColor = '#3b82f6'}
        onMouseOut={e => e.currentTarget.style.borderColor = '#1a3a6b'}
      >
        <span style={{ fontSize: 24 }}>⬆</span>
        <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>Drop CSV or click to upload</span>
        <input type="file" accept=".csv" style={{ display: 'none' }} onChange={onUpload} />
      </label>

      {/* File badge */}
      {schema && (
        <div style={{
          background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.25)',
          borderRadius: 10, padding: '10px 12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', display: 'inline-block' }} />
            <button onClick={onClear} style={{
              background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: 15, padding: 0,
            }}
              onMouseOver={e => e.currentTarget.style.color = '#f87171'}
              onMouseOut={e => e.currentTarget.style.color = '#475569'}
            >×</button>
          </div>
          <div style={{ fontSize: 12, color: '#6ee7b7', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {schema.name}
          </div>
          <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>
            {schema.rows?.toLocaleString()} rows · {schema.cols} columns
          </div>
        </div>
      )}
    </aside>
  )
}
