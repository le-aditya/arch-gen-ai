import BlueprintDiagram from './BlueprintDiagram'
import styles from './Screen4Architecture.module.css'

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
        <BlueprintDiagram
          diagram={architecture.diagrams.architecture}
          title="ARCHITECTURE"
          sheet="1 OF 2"
        />
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionLabel}>Deployment</h2>
        <BlueprintDiagram
          diagram={architecture.diagrams.deployment}
          title="DEPLOYMENT"
          sheet="2 OF 2"
        />
      </section>

      <button className={styles.navButton} onClick={onNext}>
        View report
      </button>
    </div>
  )
}
