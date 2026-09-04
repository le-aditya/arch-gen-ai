import styles from './Screen4Architecture.module.css'

function computeLevels(nodes, edges) {
  const incoming = new Map(nodes.map(n => [n.id, 0]))
  edges.forEach(e => incoming.set(e.target, (incoming.get(e.target) || 0) + 1))

  const level = new Map()
  nodes.filter(n => incoming.get(n.id) === 0).forEach(n => level.set(n.id, 0))

  let changed = true
  while (changed) {
    changed = false
    edges.forEach(e => {
      if (level.has(e.source)) {
        const candidate = level.get(e.source) + 1
        if (!level.has(e.target) || level.get(e.target) < candidate) {
          level.set(e.target, candidate)
          changed = true
        }
      }
    })
  }

  const maxLevel = Math.max(0, ...Array.from(level.values()))
  const rows = Array.from({ length: maxLevel + 1 }, () => [])
  nodes.forEach(n => rows[level.get(n.id) ?? 0].push(n))
  return rows
}

const NODE_STYLE_BY_KIND = {
  client: '',
  gateway: 'diagramNodeAccent',
  service: '',
  database: 'diagramNodeDb',
  queue: 'diagramNodeDb',
  infra: 'diagramNodeAccent',
}

function GraphDiagram({ diagram }) {
  const rows = computeLevels(diagram.nodes, diagram.edges)

  return (
    <div className={styles.diagramCard}>
      <span className={styles.diagramCaption}>{diagram.caption}</span>
      <div className={styles.diagramFlow}>
        {rows.map((row, i) => (
          <div key={i} className={styles.diagramLevel}>
            {i > 0 && <div className={styles.diagramArrowDown} />}
            <div className={styles.diagramBranch}>
              {row.map(node => (
                <div
                  key={node.id}
                  className={`${styles.diagramNode} ${styles[NODE_STYLE_BY_KIND[node.kind]] || ''}`}
                >
                  {node.label}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const STACK_LABELS = {
  frontend: 'Frontend',
  backend: 'Backend',
  database: 'Database',
  messaging: 'Messaging',
  infrastructure: 'Infrastructure',
}

export default function Screen4Architecture({ architecture, onNext }) {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Generated architecture</h1>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>Tech stack</h2>
        <div className={styles.sheet}>
          {Object.entries(architecture.tech_stack)
            .filter(([, items]) => items.length > 0)
            .map(([category, items]) => (
              <div key={category} className={styles.row}>
                <span className={styles.rowLabel}>{STACK_LABELS[category] || category}</span>
                <span className={styles.rowValue}>{items.join(' · ')}</span>
              </div>
            ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>Database</h2>
        <table className={styles.dbTable}>
          <thead>
            <tr>
              <th>Table</th>
              <th>Columns</th>
            </tr>
          </thead>
          <tbody>
            {architecture.database.tables.map(table => (
              <tr key={table.name}>
                <td className={styles.dbTableName}>{table.name}</td>
                <td className={styles.dbTableColumns}>{table.columns.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>API</h2>
        <div className={styles.apiList}>
          {architecture.apis.map((api, i) => (
            <div key={i} className={styles.apiItem}>
              <span className={`${styles.methodBadge} ${styles[`method${api.method}`]}`}>
                {api.method}
              </span>
              <span className={styles.apiPath}>{api.path}</span>
              <span className={styles.apiPurpose}>{api.purpose}</span>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>Architecture</h2>
        <GraphDiagram diagram={architecture.diagrams.architecture} />
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>Deployment</h2>
        <GraphDiagram diagram={architecture.diagrams.deployment} />
      </section>

      <button className={styles.navButton} onClick={onNext}>
        View report
      </button>
    </div>
  )
}
