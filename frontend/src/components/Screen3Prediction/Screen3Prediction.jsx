import styles from './Screen3Prediction.module.css'

export default function Screen3Prediction({ prediction, onNext }) {
  const maxImportance = Math.max(...prediction.top_factors.map(f => f.importance))

  // Older responses (and regenerated reports) carry only the winning class.
  const distribution = prediction.alternatives?.length
    ? prediction.alternatives
    : [{ architecture: prediction.architecture, probability: prediction.confidence }]

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Architecture analysis</h1>

      <div className={styles.result}>
        <span className={styles.eyebrow}>Recommendation</span>
        <div className={styles.archName}>{prediction.architecture}</div>
      </div>

      <div className={styles.distribution}>
        <span className={styles.groupLabel}>Model confidence across all classes</span>
        {distribution.map((entry, i) => {
          const pct = entry.probability * 100
          return (
            <div key={entry.architecture} className={styles.classRow} data-winner={i === 0}>
              <span className={styles.className}>{entry.architecture}</span>
              <div className={styles.classTrack}>
                <div
                  className={styles.classFill}
                  style={{ width: `${pct}%`, animationDelay: `${i * 0.08}s` }}
                />
              </div>
              <span className={styles.classValue}>{pct.toFixed(1)}%</span>
            </div>
          )
        })}
      </div>

      <div className={styles.factors}>
        <span className={styles.groupLabel}>What drove the decision</span>
        {prediction.top_factors.map(factor => (
          <div key={factor.name} className={styles.factor}>
            <div className={styles.factorHeader}>
              <span className={styles.factorName}>{factor.name}</span>
              <span className={styles.factorValue}>
                {Math.round((factor.importance / maxImportance) * 100)}%
              </span>
            </div>
            <div className={styles.factorTrack}>
              <div
                className={styles.factorFill}
                style={{ width: `${(factor.importance / maxImportance) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <button className={styles.navButton} onClick={onNext}>
        Generate specifications
      </button>
    </div>
  )
}
