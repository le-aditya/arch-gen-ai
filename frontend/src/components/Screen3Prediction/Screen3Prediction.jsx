import styles from './Screen3Prediction.module.css'

export default function Screen3Prediction({ prediction, onNext }) {
  const maxImportance = Math.max(...prediction.top_factors.map(f => f.importance))

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Architecture analysis</h1>

      <div className={styles.result}>
        <span className={styles.eyebrow}>Recommendation</span>
        <div className={styles.archName}>{prediction.architecture}</div>

        <div className={styles.confidence}>
          <span className={styles.confidenceValue}>{prediction.confidence.toFixed(2)}</span>
          <span className={styles.confidenceLabel}>confidence</span>
        </div>
      </div>

      <div className={styles.factors}>
        <span className={styles.factorsTitle}>Why</span>
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
