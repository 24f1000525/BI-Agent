import { useRef, useMemo } from 'react'

const DEFAULT_CHIPS = [
  'Show a summary overview of all columns',
  'Compare top categories by value',
  'Show distribution of the main numeric column',
  'What are the trends over time?',
  'Show a breakdown of categories as a pie chart',
]

function buildDynamicChips(schema) {
  if (!schema || !schema.columns || schema.columns.length === 0) return DEFAULT_CHIPS
  const cols = schema.columns
  const chips = []

  // Find likely numeric and categorical columns from names
  const numericHints = ['amount', 'price', 'count', 'total', 'sum', 'value', 'cost', 'revenue', 'sales', 'profit', 'quantity', 'rate', 'ratio', 'score', 'age', 'salary', 'weight', 'height']
  const dateHints = ['date', 'year', 'month', 'time', 'period', 'quarter']
  const catCols = []
  const numCols = []
  const dateCols = []

  cols.forEach(c => {
    const cl = c.toLowerCase()
    if (dateHints.some(h => cl.includes(h))) dateCols.push(c)
    else if (numericHints.some(h => cl.includes(h))) numCols.push(c)
    else catCols.push(c)
  })

  if (numCols.length > 0 && catCols.length > 0) {
    chips.push(`Compare ${numCols[0]} across different ${catCols[0]}`)
  }
  if (numCols.length > 0) {
    chips.push(`Show distribution of ${numCols[0]}`)
  }
  if (dateCols.length > 0 && numCols.length > 0) {
    chips.push(`Show trend of ${numCols[0]} over ${dateCols[0]}`)
  }
  if (catCols.length > 0) {
    chips.push(`Show breakdown of ${catCols[0]} as a pie chart`)
  }
  if (numCols.length >= 2) {
    chips.push(`Scatter plot of ${numCols[0]} vs ${numCols[1]}`)
  }
  if (chips.length < 3) {
    chips.push(`Give me an overview dashboard of this data`)
  }
  if (catCols.length > 0 && numCols.length > 0) {
    chips.push(`Top 10 ${catCols[0]} ranked by ${numCols[0]}`)
  }

  return chips.slice(0, 5)
}

export default function QueryBox({ loading, onSubmit, schema }) {
  const ref = useRef(null)

  const submit = () => {
    const q = ref.current?.value?.trim()
    if (!q) return
    onSubmit(q)
    ref.current.value = ''
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const useChip = (text) => {
    if (ref.current) ref.current.value = text
    onSubmit(text)
  }

  const chips = useMemo(() => buildDynamicChips(schema), [schema])

  return (
    <div className="anim-glow4" style={{
      background: 'linear-gradient(135deg,#0a1628ee,#0d1f3ccc)',
      border: '1px solid #2563eb66', borderRadius: 18, padding: 22, marginBottom: 20,
      boxShadow: '0 0 60px rgba(37,99,235,.12),inset 0 1px 0 #2563eb22',
      backdropFilter: 'blur(20px)',
    }}>
      <div style={{ fontSize: 10, color: '#06b6d4', letterSpacing: 3, textTransform: 'uppercase', marginBottom: 10 }}>
        ◈ Natural Language Query
      </div>
      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <span style={{ color: '#3b82f6', fontFamily: '"Space Mono",monospace', fontSize: 14, paddingTop: 8, flexShrink: 0 }}>›_</span>
        <textarea
          ref={ref}
          rows={2}
          onKeyDown={handleKey}
          placeholder="Ask anything about your data…"
          style={{
            flex: 1, background: 'transparent', border: 'none', outline: 'none',
            color: '#e2e8f0', fontFamily: '"Space Mono",monospace', fontSize: 14,
            resize: 'none', lineHeight: 1.5,
          }}
        />
        <button
          onClick={submit}
          disabled={loading}
          style={{
            background: loading ? '#1a3a6b' : 'linear-gradient(135deg,#3b82f6,#2563eb)',
            border: 'none', borderRadius: 11, padding: '10px 18px', color: '#fff',
            cursor: loading ? 'not-allowed' : 'pointer', fontSize: 18,
            boxShadow: loading ? 'none' : '0 0 20px #3b82f666', flexShrink: 0,
            transition: 'all .2s',
          }}
          onMouseOver={e => !loading && (e.currentTarget.style.filter = 'brightness(1.15)')}
          onMouseOut={e => (e.currentTarget.style.filter = '')}
        >→</button>
      </div>

      {/* Chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginTop: 14, alignItems: 'center' }}>
        <span style={{ fontSize: 10, color: '#64748b' }}>Try:</span>
        {chips.map((c, i) => (
          <span
            key={i}
            onClick={() => useChip(c)}
            style={{
              background: '#0d1f3c88', border: '1px solid #1a3a6b', borderRadius: 7,
              padding: '5px 10px', fontSize: 10, color: '#64748b', cursor: 'pointer',
              transition: 'all .2s', fontFamily: 'Syne,sans-serif',
            }}
            onMouseOver={e => {
              e.currentTarget.style.background = '#2563eb22'
              e.currentTarget.style.borderColor = '#3b82f6'
              e.currentTarget.style.color = '#e2e8f0'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseOut={e => {
              e.currentTarget.style.background = '#0d1f3c88'
              e.currentTarget.style.borderColor = '#1a3a6b'
              e.currentTarget.style.color = '#64748b'
              e.currentTarget.style.transform = ''
            }}
          >{c}</span>
        ))}
      </div>
    </div>
  )
}
