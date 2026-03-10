// Power BI-inspired color palette
const COLORS = [
  '#118DFF','#12239E','#E66C37','#6B007B','#E044A7',
  '#744EC2','#D9B300','#D64550','#197278','#1AAB40',
  '#01B8AA','#FD625E','#F2C80F','#8AD4EB','#FE9666',
  '#A66999','#3599B8','#DFBFBF','#4AC5BB','#5F6B6D',
]
const ACCENT = [
  '#118DFF','#E66C37','#6B007B','#D9B300','#1AAB40',
  '#D64550','#744EC2','#01B8AA','#E044A7','#197278',
]

import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, RadialLinearScale, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Line, Bar, Pie, Doughnut, Radar, PolarArea } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, RadialLinearScale, Title, Tooltip, Legend, Filler
)

const chartOptions = {
  responsive: true,
  animation: { duration: 900, easing: 'easeOutQuart' },
  plugins: {
    legend: {
      labels: { color: '#c8d0dc', font: { family: 'Syne', size: 11, weight: 500 }, padding: 18, usePointStyle: true, pointStyle: 'rectRounded' },
      position: 'bottom',
    },
    tooltip: {
      backgroundColor: '#1b2a4a', borderColor: '#334d80', borderWidth: 1,
      titleColor: '#f1f5f9', bodyColor: '#cbd5e1', padding: 12, cornerRadius: 8,
      titleFont: { family: 'Syne', size: 13, weight: 700 },
      bodyFont: { family: 'Space Mono', size: 11 },
    },
  },
  scales: {
    x: { ticks: { color: '#8896ab', font: { family: 'Syne', size: 10 } }, grid: { color: '#1e3a5f18' }, border: { color: '#1e3a5f44' } },
    y: { ticks: { color: '#8896ab', font: { family: 'Syne', size: 10 } }, grid: { color: '#1e3a5f18' }, border: { color: '#1e3a5f44' } },
  },
}

const noScalesOptions = {
  ...chartOptions,
  scales: {},
}

function buildDatasets(chart) {
  const highlight = chart.highlight || null

  const matchesRule = (v) => {
    if (!highlight || v === null || v === undefined || Number.isNaN(Number(v))) return false
    const threshold = Number(highlight.threshold)
    if (Number.isNaN(threshold)) return false

    const raw = Number(v)
    const compareVal = Math.abs(raw) <= 1.5 && threshold > 1.5 ? raw * 100 : raw
    const op = highlight.operator || 'lt'

    if (op === 'lt') return compareVal < threshold
    if (op === 'lte') return compareVal <= threshold
    if (op === 'gt') return compareVal > threshold
    if (op === 'gte') return compareVal >= threshold
    return false
  }

  const hiColor = (highlight && highlight.color) || '#D64550'
  const isMultiSerie = (chart.datasets || []).length > 1
  return (chart.datasets || []).map((ds, di) => {
    const baseColor = ds.color || COLORS[di % COLORS.length]
    const isLine = chart.type === 'line' || chart.type === 'area'
    const isPie  = ['pie','doughnut','polarArea'].includes(chart.type)
    const isScatter = chart.type === 'scatter'
    const values = ds.data || []

    const pointwiseBg = values.map((value, vi) => {
      if (!highlight) {
        if (isPie) return COLORS[vi % COLORS.length] + 'cc'
        if (isLine) return baseColor + '33'
        return isMultiSerie ? baseColor + 'cc' : COLORS[di % COLORS.length] + 'cc'
      }
      return matchesRule(value) ? hiColor + 'cc' : (isPie ? COLORS[vi % COLORS.length] + 'cc' : (isLine ? baseColor + '33' : baseColor + 'cc'))
    })

    const pointwiseBorder = values.map((value, vi) => {
      if (!highlight) {
        if (isPie) return COLORS[vi % COLORS.length]
        if (isLine || chart.type === 'radar') return baseColor
        return isMultiSerie ? baseColor : COLORS[di % COLORS.length]
      }
      return matchesRule(value) ? hiColor : (isPie ? COLORS[vi % COLORS.length] : baseColor)
    })

    return {
      label: ds.label || `Series ${di + 1}`,
      data: values,
      backgroundColor: isPie
        ? pointwiseBg
        : isLine
          ? baseColor + '33'
          : (highlight ? pointwiseBg : (isMultiSerie ? baseColor + 'cc' : COLORS[di % COLORS.length] + 'cc')),
      borderColor: isPie
        ? pointwiseBorder
        : isLine || chart.type === 'radar'
          ? baseColor
          : (highlight ? pointwiseBorder : (isMultiSerie ? baseColor : COLORS[di % COLORS.length])),
      borderWidth: chart.type === 'bar' ? 0 : 2.5,
      fill: isLine,
      tension: 0.4,
      pointRadius: isLine ? 4 : 0,
      pointHoverRadius: 7,
      pointBackgroundColor: highlight ? pointwiseBorder : baseColor,
      pointBorderColor: highlight ? pointwiseBorder : baseColor,
      borderRadius: chart.type === 'bar' ? 6 : 0,
      hoverBackgroundColor: isPie
        ? (chart.labels || []).map((_, li) => COLORS[li % COLORS.length])
        : baseColor,
      // For scatter charts, allow per-point highlight color.
      ...(isScatter ? { pointBackgroundColor: highlight ? pointwiseBorder : baseColor } : {}),
    }
  })
}

function MatrixWrapper({ chart, idx }) {
  const accent = ACCENT[idx % ACCENT.length]
  const matrix = chart.matrix || {}
  const rows = matrix.rows || []
  const columns = matrix.columns || []
  const values = matrix.values || []
  const unit = matrix.unit || ''
  const rule = matrix.highlight || { operator: 'lt', threshold: 85, color: '#D64550' }

  const isHighlighted = (v) => {
    if (v === null || v === undefined || Number.isNaN(v)) return false
    if (rule.operator === 'lt') return v < Number(rule.threshold)
    if (rule.operator === 'lte') return v <= Number(rule.threshold)
    if (rule.operator === 'gt') return v > Number(rule.threshold)
    if (rule.operator === 'gte') return v >= Number(rule.threshold)
    return false
  }

  return (
    <div className="anim-fadeUp" style={{
      width: '100%', minWidth: 320,
      background: 'linear-gradient(145deg,#0c1a30f0,#0f2340e8)',
      border: '1px solid #1e3a5f88', borderRadius: 16, padding: 20,
      position: 'relative', overflow: 'hidden', backdropFilter: 'blur(12px)',
      boxShadow: '0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)',
    }}>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 3,
        background: `linear-gradient(90deg,transparent,${accent},transparent)`,
        opacity: 0.8,
      }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: accent, boxShadow: `0 0 8px ${accent}66`, flexShrink: 0 }} />
        <div style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9' }}>{chart.title}</div>
      </div>
      <div style={{ fontSize: 11, color: '#7a8ba8', marginBottom: 12, paddingLeft: 16 }}>{chart.description}</div>

      <div style={{ overflowX: 'auto', border: '1px solid #1e3a5f66', borderRadius: 10 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 720 }}>
          <thead>
            <tr style={{ background: '#132949' }}>
              <th style={{ position: 'sticky', left: 0, background: '#132949', zIndex: 1, padding: '8px 10px', borderBottom: '1px solid #1e3a5f88', color: '#dbe7f6', fontSize: 11, textAlign: 'left' }}>
                {matrix.rowHeader || 'Row'}
              </th>
              {columns.map((col) => (
                <th key={col} style={{ padding: '8px 10px', borderBottom: '1px solid #1e3a5f88', color: '#dbe7f6', fontSize: 11, textAlign: 'right', whiteSpace: 'nowrap' }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, ri) => (
              <tr key={r} style={{ background: ri % 2 === 0 ? '#0f2340aa' : '#0e2038aa' }}>
                <td style={{ position: 'sticky', left: 0, background: ri % 2 === 0 ? '#0f2340' : '#0e2038', zIndex: 1, padding: '8px 10px', borderBottom: '1px solid #1e3a5f55', color: '#d7e2f0', fontSize: 11, fontWeight: 600, textAlign: 'left', whiteSpace: 'nowrap' }}>
                  {r}
                </td>
                {columns.map((_, ci) => {
                  const v = values?.[ri]?.[ci]
                  const hi = isHighlighted(v)
                  return (
                    <td
                      key={`${r}-${ci}`}
                      style={{
                        padding: '8px 10px',
                        borderBottom: '1px solid #1e3a5f44',
                        textAlign: 'right',
                        fontFamily: '"Space Mono",monospace',
                        fontSize: 11,
                        color: hi ? '#ffd9dd' : '#d3deee',
                        background: hi ? `${rule.color || '#D64550'}33` : 'transparent',
                        borderLeft: hi ? `2px solid ${rule.color || '#D64550'}` : 'none',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {v === null || v === undefined ? '-' : `${Number(v).toFixed(2)}${unit}`}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ marginTop: 10, fontSize: 11, color: '#9db0c8' }}>
        Highlight rule: values {rule.operator || 'lt'} {rule.threshold}{unit} shown in red.
      </div>
    </div>
  )
}

function ChartWrapper({ chart, idx }) {
  if (chart.type === 'matrix') {
    return <MatrixWrapper chart={chart} idx={idx} />
  }

  const accent   = ACCENT[idx % ACCENT.length]
  const isHalf   = chart.width === 'half'
  const isThird  = chart.width === 'third'
  const width    = isThird ? 'calc(33.33% - 10px)' : isHalf ? 'calc(50% - 7px)' : '100%'
  const isPie    = ['pie','doughnut','polarArea','radar'].includes(chart.type)

  const data = { labels: chart.labels || [], datasets: buildDatasets(chart) }
  const opts = isPie ? noScalesOptions : chartOptions

  const typeMap = { line: Line, area: Line, bar: Bar, pie: Pie, doughnut: Doughnut, radar: Radar, polarArea: PolarArea }
  const Component = typeMap[chart.type] || Bar

  return (
    <div className="anim-fadeUp" style={{
      width, minWidth: 280,
      background: 'linear-gradient(145deg,#0c1a30f0,#0f2340e8)',
      border: '1px solid #1e3a5f88', borderRadius: 16, padding: 24,
      position: 'relative', overflow: 'hidden', backdropFilter: 'blur(12px)',
      animationDelay: `${idx * 0.12}s`,
      boxShadow: '0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)',
      transition: 'border-color 0.3s, box-shadow 0.3s',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.borderColor = accent + '88'
      e.currentTarget.style.boxShadow = `0 4px 32px rgba(0,0,0,0.35), 0 0 20px ${accent}15, inset 0 1px 0 rgba(255,255,255,0.05)`
    }}
    onMouseLeave={e => {
      e.currentTarget.style.borderColor = '#1e3a5f88'
      e.currentTarget.style.boxShadow = '0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)'
    }}
    >
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 3,
        background: `linear-gradient(90deg,transparent,${accent},transparent)`,
        opacity: 0.8,
      }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: accent, boxShadow: `0 0 8px ${accent}66`, flexShrink: 0 }} />
        <div style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9' }}>{chart.title}</div>
      </div>
      <div style={{ fontSize: 11, color: '#7a8ba8', marginBottom: 16, paddingLeft: 16 }}>{chart.description}</div>
      {chart.highlight && (
        <div style={{ marginBottom: 10, fontSize: 11, color: '#9db0c8' }}>
          Highlight rule: values {chart.highlight.operator || 'lt'} {chart.highlight.threshold} shown in {chart.highlight.color || '#D64550'}.
        </div>
      )}
      <Component data={data} options={{ ...opts, maintainAspectRatio: true }} style={{ maxHeight: 300 }} />
    </div>
  )
}

export default function ChartsGrid({ charts }) {
  if (!charts || charts.length === 0) return null
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 14 }}>
      {charts.map((chart, idx) => (
        <ChartWrapper key={chart.id || idx} chart={chart} idx={idx} />
      ))}
    </div>
  )
}
