import ChartsGrid from './ChartsGrid'

const UploadIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#fi1)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <defs><linearGradient id="fi1" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse"><stop stopColor="#38bdf8"/><stop offset="1" stopColor="#818cf8"/></linearGradient></defs>
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
)

const AskIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#fi2)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <defs><linearGradient id="fi2" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse"><stop stopColor="#a78bfa"/><stop offset="1" stopColor="#38bdf8"/></linearGradient></defs>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    <line x1="9" y1="10" x2="15" y2="10"/>
    <line x1="9" y1="14" x2="13" y2="14"/>
  </svg>
)

const VisualizeIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#fi3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <defs><linearGradient id="fi3" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse"><stop stopColor="#3b82f6"/><stop offset="1" stopColor="#8b5cf6"/></linearGradient></defs>
    <rect x="18" y="3" width="4" height="18" rx="1"/>
    <rect x="10" y="8" width="4" height="13" rx="1"/>
    <rect x="2" y="13" width="4" height="8" rx="1"/>
    <polyline points="2,12 10,6 18,2" opacity="0.6"/>
  </svg>
)

const DiscoverIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="url(#fi4)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <defs><linearGradient id="fi4" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse"><stop stopColor="#34d399"/><stop offset="1" stopColor="#38bdf8"/></linearGradient></defs>
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    <path d="M11 8v6M8 11h6" opacity="0.7"/>
  </svg>
)

const features = [
  { Icon: UploadIcon, title: 'Upload', desc: 'Drop any CSV file and start instantly' },
  { Icon: AskIcon, title: 'Ask', desc: 'Chat in plain English to query your data' },
  { Icon: VisualizeIcon, title: 'Visualize', desc: 'Auto-generated charts for every question' },
  { Icon: DiscoverIcon, title: 'Discover', desc: 'AI finds patterns and trends you\'d miss' },
]

function LandingPage() {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', minHeight: 'calc(100vh - 64px)',
      padding: '40px 20px', textAlign: 'center',
    }}>
      {/* Hero logo mark */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 36 }}>
        <svg width="60" height="60" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="ol1" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#3b82f6"/>
              <stop offset="100%" stopColor="#8b5cf6"/>
            </linearGradient>
            <linearGradient id="ol2" x1="0" y1="0" x2="34" y2="34" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38bdf8"/>
              <stop offset="100%" stopColor="#3b82f6"/>
            </linearGradient>
          </defs>
          <rect width="34" height="34" rx="9" fill="url(#ol1)" opacity="0.15"/>
          <rect width="34" height="34" rx="9" fill="none" stroke="url(#ol1)" strokeWidth="1.2" opacity="0.5"/>
          <rect x="7" y="20" width="4.5" height="8" rx="1.5" fill="url(#ol2)" opacity="0.7"/>
          <rect x="14.75" y="13" width="4.5" height="15" rx="1.5" fill="url(#ol1)"/>
          <rect x="22.5" y="7" width="4.5" height="21" rx="1.5" fill="url(#ol2)"/>
          <polyline points="9.25,19 17,12 24.75,6" fill="none" stroke="#a78bfa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.9"/>
          <circle cx="24.75" cy="6" r="1.8" fill="#a78bfa"/>
        </svg>
        <div style={{ textAlign: 'left', lineHeight: 1 }}>
          <div style={{
            fontSize: 10, fontWeight: 600, letterSpacing: '0.2em',
            color: '#4f6a99', textTransform: 'uppercase', marginBottom: 6,
          }}>AI-POWERED DATA ANALYSIS</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%', background: '#818cf8',
              boxShadow: '0 0 8px #818cf8', flexShrink: 0, display: 'inline-block',
            }} />
            <span style={{
              fontSize: 12, color: '#a5b4fc', fontWeight: 600,
              fontFamily: '"Space Mono",monospace', letterSpacing: '0.05em',
            }}>LIVE</span>
          </div>
        </div>
      </div>

      {/* Hero title */}
      <h1 style={{
        fontSize: 'clamp(36px, 6vw, 68px)', fontWeight: 800, margin: '0 0 16px',
        lineHeight: 1.1, letterSpacing: '-0.02em',
        background: 'linear-gradient(135deg, #e2e8f0 0%, #818cf8 50%, #38bdf8 100%)',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
      }}>
        DataLens AI
      </h1>

      {/* Subtitle */}
      <p style={{
        fontSize: 'clamp(16px, 2.5vw, 22px)', color: '#94a3b8', margin: '0 0 12px',
        fontWeight: 400, letterSpacing: '0.01em',
      }}>
        Conversational AI for Data Analysis
      </p>

      {/* Tagline */}
      <p style={{
        fontSize: 'clamp(20px, 3.5vw, 32px)', fontWeight: 700,
        color: '#e2e8f0', margin: '0 0 20px', letterSpacing: '-0.01em',
      }}>
        Ask your data anything
      </p>

      {/* Description */}
      <p style={{
        fontSize: 15, color: '#64748b', lineHeight: 1.75,
        maxWidth: 520, margin: '0 0 56px',
      }}>
        Upload a CSV, then chat with AI to uncover insights, generate charts,
        and explore trends — no code needed.
      </p>

      {/* Feature cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 16, width: '100%', maxWidth: 860,
      }}>
        {features.map(f => (
          <div key={f.title} style={{
            background: 'rgba(15,23,42,0.6)',
            border: '1px solid rgba(99,102,241,0.18)',
            borderRadius: 16, padding: '28px 22px',
            backdropFilter: 'blur(12px)',
            transition: 'border-color 0.2s, transform 0.2s',
          }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'rgba(129,140,248,0.5)'
              e.currentTarget.style.transform = 'translateY(-3px)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'rgba(99,102,241,0.18)'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.25)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 14px',
            }}>
              <f.Icon />
            </div>
            <h3 style={{
              fontSize: 15, fontWeight: 700, color: '#e2e8f0', margin: '0 0 8px',
            }}>
              {f.title}
            </h3>
            <p style={{ fontSize: 13, color: '#64748b', margin: 0, lineHeight: 1.6 }}>
              {f.desc}
            </p>
          </div>
        ))}
      </div>

      {/* Bottom hint */}
      <p style={{ marginTop: 48, fontSize: 13, color: '#334155' }}>
        Click <strong style={{ color: '#818cf8' }}>Upload CSV</strong> in the navbar to begin
      </p>
    </div>
  )
}

export default function Overview({ data, loading, schema }) {
  if (!schema) {
    return <LandingPage />
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <div style={{ width: 48, height: 48, position: 'relative', margin: '0 auto 16px' }}>
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
          Analyzing dataset…
        </p>
      </div>
    )
  }

  if (!data) return null

  const { kpi, key_columns, charts } = data

  return (
    <div>
      {/* ── KPI Cards ── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: 14, marginBottom: 28,
      }}>
        <KpiCard label="Rows" value={kpi.rows?.toLocaleString()} color="#118DFF" icon="📋" />
        <KpiCard label="Columns" value={kpi.cols} color="#01B8AA" icon="📐" />
        <KpiCard label="Missing" value={kpi.missing?.toLocaleString()} color="#D64550" icon="⚠" />
        <KpiCard
          label="Quality"
          value={`${kpi.completeness}%`}
          sub={`${kpi.duplicates?.toLocaleString()} duplicates`}
          color="#1AAB40"
          icon="✅"
        />
      </div>

      {/* ── Key Columns ── */}
      {key_columns?.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 10, color: '#94a3b8', letterSpacing: 3, textTransform: 'uppercase', fontWeight: 600, marginBottom: 12 }}>
            Key Columns
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {key_columns.map(col => (
              <span key={col} style={{
                display: 'inline-block', padding: '5px 14px',
                borderRadius: 999, background: '#1e293b',
                border: '1px solid #334155', color: '#cbd5e1',
                fontSize: 12, fontWeight: 500,
              }}>{col}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── Auto-Charts ── */}
      {charts?.length > 0 && (
        <div>
          <div style={{ fontSize: 10, color: '#94a3b8', letterSpacing: 3, textTransform: 'uppercase', fontWeight: 600, marginBottom: 16 }}>
            Dataset Overview
          </div>
          <ChartsGrid charts={charts} />
        </div>
      )}
    </div>
  )
}

function KpiCard({ label, value, sub, color, icon }) {
  return (
    <div className="anim-fadeUp" style={{
      background: 'linear-gradient(135deg,#0a1628dd,#0d1f3caa)',
      border: `1px solid ${color}44`, borderRadius: 14, padding: '18px 20px',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: -15, right: -15, width: 60, height: 60,
        borderRadius: '50%', background: color, filter: 'blur(15px)', opacity: .15,
      }} />
      <div style={{ fontSize: 20, marginBottom: 8 }}>{icon}</div>
      <div style={{ fontSize: 22, fontWeight: 800, fontFamily: '"Space Mono",monospace', color, letterSpacing: -1 }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: '#64748b', marginTop: 3, textTransform: 'uppercase', letterSpacing: 2 }}>
        {label}
      </div>
      {sub && (
        <div style={{ fontSize: 10, color: '#475569', marginTop: 4 }}>{sub}</div>
      )}
    </div>
  )
}
