import styles from './Screen2Requirements.module.css'

export default function Screen2Requirements({ requirements, onNext }) {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Requirements</h1>

      <div className={styles.sheet}>
        <div className={styles.row}>
          <span className={styles.label}>Domain</span>
          <span className={styles.value}>{requirements.domain}</span>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Actors</span>
          <div className={styles.list}>
            {requirements.actors.map(actor => (
              <span key={actor} className={styles.item}>{actor}</span>
            ))}
          </div>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Modules</span>
          <div className={styles.list}>
            {requirements.modules.map(mod => (
              <span key={mod} className={styles.item}>{mod}</span>
            ))}
          </div>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Real-time</span>
          <span className={styles.value} data-flag={requirements.real_time}>
            {requirements.real_time ? 'True' : 'False'}
          </span>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Payment</span>
          <span className={styles.value} data-flag={requirements.payment}>
            {requirements.payment ? 'True' : 'False'}
          </span>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Integrations</span>
          <div className={styles.list}>
            {requirements.external_integrations.length > 0 ? (
              requirements.external_integrations.map(int => (
                <span key={int} className={styles.item}>{int}</span>
              ))
            ) : (
              <span className={styles.itemMuted}>none</span>
            )}
          </div>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>Data complexity</span>
          <span className={styles.value}>{requirements.data_complexity}</span>
        </div>
      </div>

      <button className={styles.navButton} onClick={onNext}>
        Classify architecture
      </button>
    </div>
  )
}
