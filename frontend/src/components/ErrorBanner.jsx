export default function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div style={{
      background: '#1f0a0a', border: '1px solid #7f1d1d', borderRadius: 10,
      padding: '14px 18px', color: '#fca5a5', fontSize: 13, marginBottom: 16,
    }}>
      ⚠ {message}
    </div>
  )
}
