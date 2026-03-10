export default function EmptyState({ onUpload }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', minHeight: 360, textAlign: 'center', padding: '40px 20px',
    }}>
      <div style={{
        width: 72, height: 72, borderRadius: 18, marginBottom: 20,
        background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32,
      }}>📂</div>
      <h2 style={{
        fontSize: 22, fontWeight: 700, margin: '0 0 10px',
        background: 'linear-gradient(90deg,#3b82f6,#8b5cf6)',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
      }}>Upload a CSV to get started</h2>
      <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.7, maxWidth: 400, margin: '0 0 24px' }}>
        Upload any CSV file to automatically generate an overview with key statistics and visualizations.
      </p>
      <label style={{
        background: 'linear-gradient(135deg,#3b82f6,#2563eb)', borderRadius: 10,
        padding: '10px 24px', fontSize: 13, color: '#fff', cursor: 'pointer', fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', gap: 8,
      }}>
        ⬆ Upload CSV
        <input type="file" accept=".csv" style={{ display: 'none' }} onChange={onUpload} />
      </label>
    </div>
  )
}
