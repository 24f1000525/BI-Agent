function StatCard({ label, value, sub, color, icon }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg,#0a1628ee,#0d1f3ccc)',
      border: `1px solid ${color}33`,
      borderRadius: 14, padding: '18px 20px',
      display: 'flex', alignItems: 'center', gap: 14,
      flex: 1, minWidth: 140,
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10, flexShrink: 0,
        background: `${color}22`, border: `1px solid ${color}44`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
      }}>{icon}</div>
      <div>
        <div style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', lineHeight: 1 }}>{value ?? '—'}</div>
        {sub && <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>{sub}</div>}
        <div style={{ fontSize: 11, color: color, fontWeight: 600, marginTop: 3, letterSpacing: '0.05em' }}>{label}</div>
      </div>
    </div>
  )
}

export default function StatsGrid({ schema }) {
  if (!schema) return null
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginBottom: 28 }}>
      <StatCard label="Data Source" value={schema.name} color="#3b82f6" icon="📁" />
      <StatCard label="Total Records" value={schema.rows?.toLocaleString()} color="#06b6d4" icon="📋" />
      <StatCard label="Dimensions" value={schema.cols} color="#8b5cf6" icon="📐" />
      <StatCard label="Status" value="Ready" color="#10b981" icon="✅" />
    </div>
  )
}
