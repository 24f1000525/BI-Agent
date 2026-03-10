export default function Navbar({ schema, activeTab, onTabChange, onUpload, onClear }) {
  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'linear-gradient(90deg,#0a1628f2,#0d1f3cf2)',
      borderBottom: '1px solid #1a3a6b55',
      backdropFilter: 'blur(20px)',
      padding: '0 28px',
      display: 'flex', alignItems: 'center', gap: 0,
      height: 60,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginRight: 32 }}>
        <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="nl1" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#3b82f6"/>
              <stop offset="100%" stopColor="#8b5cf6"/>
            </linearGradient>
            <linearGradient id="nl2" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38bdf8"/>
              <stop offset="100%" stopColor="#3b82f6"/>
            </linearGradient>
          </defs>
          <rect width="34" height="34" rx="9" fill="url(#nl1)" opacity="0.15"/>
          <rect width="34" height="34" rx="9" fill="none" stroke="url(#nl1)" strokeWidth="1.2" opacity="0.5"/>
          <rect x="7" y="20" width="4.5" height="8" rx="1.5" fill="url(#nl2)" opacity="0.7"/>
          <rect x="14.75" y="13" width="4.5" height="15" rx="1.5" fill="url(#nl1)"/>
          <rect x="22.5" y="7" width="4.5" height="21" rx="1.5" fill="url(#nl2)"/>
          <polyline points="9.25,19 17,12 24.75,6" fill="none" stroke="#a78bfa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
          <circle cx="24.75" cy="6" r="1.8" fill="#a78bfa"/>
        </svg>
        <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
          <span style={{
            fontSize: 15, fontWeight: 800, letterSpacing: '-0.3px',
            background: 'linear-gradient(90deg,#e2e8f0,#a5b4fc)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>DataLens</span>
          <span style={{
            fontSize: 9.5, fontWeight: 600, letterSpacing: '0.18em',
            color: '#4f6a99', textTransform: 'uppercase', marginTop: 2,
          }}>AI · Analytics</span>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', height: '100%', gap: 0 }}>
        {['overview', 'chat'].map(tab => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            style={{
              height: '100%', padding: '0 22px',
              background: 'transparent', border: 'none',
              borderBottom: activeTab === tab ? '2px solid #818cf8' : '2px solid transparent',
              color: activeTab === tab ? '#818cf8' : '#64748b',
              fontWeight: 600, fontSize: 13, cursor: 'pointer',
              fontFamily: 'Syne, sans-serif', textTransform: 'capitalize',
              transition: 'color .2s',
            }}
          >{tab}</button>
        ))}
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* File badge */}
      {schema && (
        <div style={{
          background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.25)',
          borderRadius: 8, padding: '5px 12px', display: 'flex', alignItems: 'center', gap: 7,
          marginRight: 12, maxWidth: 260,
        }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', flexShrink: 0 }} />
          <span style={{ fontSize: 11, color: '#6ee7b7', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {schema.name}
          </span>
          <span style={{ fontSize: 10, color: '#475569', whiteSpace: 'nowrap' }}>
            {schema.rows?.toLocaleString()} rows
          </span>
          <button
            onClick={onClear}
            title="Clear data"
            style={{
              background: 'none', border: 'none', color: '#475569',
              cursor: 'pointer', fontSize: 14, padding: 0, lineHeight: 1, marginLeft: 2,
              transition: 'color .2s',
            }}
            onMouseOver={e => e.currentTarget.style.color = '#f87171'}
            onMouseOut={e => e.currentTarget.style.color = '#475569'}
          >×</button>
        </div>
      )}

      {/* Upload button */}
      <label style={{
        background: 'linear-gradient(135deg,#3b82f6,#2563eb)',
        borderRadius: 8, padding: '7px 16px',
        fontSize: 12, color: '#fff', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600,
        transition: 'filter .2s', whiteSpace: 'nowrap',
        boxShadow: '0 0 18px #3b82f644',
      }}
        onMouseOver={e => e.currentTarget.style.filter = 'brightness(1.15)'}
        onMouseOut={e => e.currentTarget.style.filter = ''}
      >
        <input type="file" accept=".csv" style={{ display: 'none' }} onChange={onUpload} />
        ⬆ Upload CSV
      </label>
    </nav>
  )
}
