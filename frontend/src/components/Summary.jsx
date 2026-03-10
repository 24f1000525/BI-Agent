export default function Summary({ text }) {
  if (!text) return null
  return (
    <div style={{
      background: 'linear-gradient(135deg,#0a162899,#0d1f3ccc)',
      border: '1px solid #1a3a6b',
      borderLeft: '3px solid #3b82f6',
      borderRadius: 12, padding: '14px 18px', marginBottom: 20,
      fontSize: 13, color: '#cbd5e1', lineHeight: 1.7,
    }}>
      <span style={{
        fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
        textTransform: 'uppercase', color: '#3b82f6', display: 'block', marginBottom: 6,
      }}>◈ AI Summary</span>
      {text}
    </div>
  )
}
