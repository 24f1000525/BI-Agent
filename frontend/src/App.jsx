import { useState, useEffect, useCallback, useRef } from 'react'
import ThreeBackground from './components/ThreeBackground'
import Navbar from './components/Navbar'
import Overview from './components/Overview'
import QueryBox from './components/QueryBox'
import Loading from './components/Loading'
import ChartsGrid from './components/ChartsGrid'
import ErrorBanner from './components/ErrorBanner'

export default function App() {
  const [schema, setSchema] = useState(null)
  const [overviewData, setOverviewData] = useState(null)
  const [overviewLoading, setOverviewLoading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [activeTab, setActiveTab] = useState('overview')
  const chatBottomRef = useRef(null)

  const fetchOverview = async () => {
    setOverviewLoading(true)
    try {
      const r = await fetch('/api/overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: 'default' }),
      })
      const data = await r.json()
      if (r.ok) setOverviewData(data)
    } catch (_) {}
    finally { setOverviewLoading(false) }
  }

  useEffect(() => {
    if (activeTab === 'chat') {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [history, activeTab])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    // Reset input so same file can be re-uploaded
    e.target.value = ''
    const form = new FormData()
    form.append('file', file)
    form.append('session_id', 'default')
    setError('')
    try {
      const r = await fetch('/api/upload', { method: 'POST', body: form })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setSchema(data)
      setHistory([])
      setActiveTab('overview')
      await fetchOverview()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleClear = () => {
    setSchema(null)
    setOverviewData(null)
    setHistory([])
    setError('')
  }

  const handleQuery = useCallback(async (query) => {
    if (!query) return
    setError('')
    setLoading(true)
    setActiveTab('chat')

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000)

    try {
      const r = await fetch('/api/query', {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          session_id: 'default',
          conversation_history: history.slice(-6),
        }),
      })
      clearTimeout(timeoutId)
      const text = await r.text()
      if (!text) throw new Error('Server returned an empty response')
      let data
      try { data = JSON.parse(text) } catch { throw new Error('Server returned invalid JSON') }
      if (!r.ok) throw new Error(data.error || `Server error ${r.status}`)

      setHistory(prev => [
        ...prev,
        { role: 'user', content: query },
        { role: 'assistant', content: data.summary || '', charts: data.charts || [] },
      ])
    } catch (err) {
      clearTimeout(timeoutId)
      const msg = err.name === 'AbortError' ? 'Request timed out (120s). Try a simpler query.' : err.message
      setError(msg)
      setHistory(prev => [
        ...prev,
        { role: 'user', content: query },
        { role: 'assistant', content: `⚠ ${msg}`, charts: [] },
      ])
    } finally {
      setLoading(false)
    }
  }, [history])

  return (
    <>
      <ThreeBackground />
      <div className="scan-line" />

      <div style={{ position: 'relative', zIndex: 2, minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* â”€â”€ Navbar â”€â”€ */}
        <Navbar
          schema={schema}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onUpload={handleUpload}
          onClear={handleClear}
        />

        {/* â”€â”€ Page body â”€â”€ */}
        <div style={{ maxWidth: 1300, margin: '0 auto', width: '100%', padding: '32px 28px 80px' }}>
          <ErrorBanner message={error} />

          {/* â”€â”€ Overview Tab â”€â”€ */}
          {activeTab === 'overview' && (
            <>
              <Overview data={overviewData} loading={overviewLoading} schema={schema} />
              {schema && (
                <div style={{ marginTop: 32, borderTop: '1px solid #1a3a6b44', paddingTop: 28 }}>
                  <div style={{ fontSize: 10, color: '#94a3b8', letterSpacing: 3, textTransform: 'uppercase', fontWeight: 600, marginBottom: 16 }}>
                    â—ˆ Ask a question about your data
                  </div>
                  <QueryBox loading={loading} onSubmit={handleQuery} schema={schema} />
                </div>
              )}
            </>
          )}

          {/* â”€â”€ Chat Tab â”€â”€ */}
          {activeTab === 'chat' && (
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: 10, color: '#64748b', letterSpacing: 3, textTransform: 'uppercase', marginBottom: 20, fontWeight: 600 }}>
                â—ˆ Chat
              </div>

              {/* Messages */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 28 }}>
                {history.length === 0 && !loading && (
                  <div style={{ textAlign: 'center', padding: '48px 20px', color: '#475569', fontSize: 13, lineHeight: 1.8 }}>
                    Ask a question below to start the conversation
                  </div>
                )}

                {history.map((msg, i) => (
                  <div key={i}>
                    {msg.role === 'user' ? (
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                        <div style={{
                          background: '#1a2236', border: '1px solid #334155',
                          borderLeft: '3px solid #818cf8',
                          borderRadius: 14, padding: '12px 18px',
                          fontSize: 13, color: '#e2e8f0', maxWidth: '75%', lineHeight: 1.6,
                        }}>
                          {msg.content}
                        </div>
                        <span style={{ flexShrink: 0, marginTop: 4, width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #818cf8, #6366f1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                        </span>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: 10 }}>
                        <span style={{ flexShrink: 0, marginTop: 4, width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #34d399, #10b981)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L9 9l-7 1 5 5-1.5 7L12 18l6.5 4L17 15l5-5-7-1z"/></svg>
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{
                            background: '#1e293b', border: '1px solid #334155',
                            borderLeft: '3px solid #34d399',
                            borderRadius: 14, padding: '12px 18px',
                            fontSize: 13, color: '#e2e8f0', lineHeight: 1.6, marginBottom: 10,
                          }}>
                            {msg.content}
                          </div>
                          {msg.charts?.length > 0 && <ChartsGrid charts={msg.charts} />}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div style={{ display: 'flex', gap: 10 }}>
                    <span style={{ flexShrink: 0, width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #34d399, #10b981)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L9 9l-7 1 5 5-1.5 7L12 18l6.5 4L17 15l5-5-7-1z"/></svg>
                    </span>
                    <div style={{
                      background: '#1e293b', border: '1px solid #334155',
                      borderLeft: '3px solid #34d399',
                      borderRadius: 14, padding: '14px 18px',
                    }}>
                      <Loading inline />
                    </div>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              <QueryBox loading={loading} onSubmit={handleQuery} schema={schema} />
            </div>
          )}
        </div>
      </div>
    </>
  )
}
