import { useState } from 'react'
import { downloadReport } from '../../services/api'
import styles from './Screen5Report.module.css'

export default function Screen5Report({ report, prediction, architecture, onRestart }) {
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState(null)

  const handleDownload = async () => {
    setDownloading(true)
    setDownloadError(null)
    try {
      await downloadReport(report.id)
    } catch (err) {
      setDownloadError(err.message)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Report</h1>

      <div className={styles.summary}>
        <span className={styles.eyebrow}>Recommended architecture</span>
        <div className={styles.archName}>{prediction.architecture}</div>
        <p className={styles.summaryText}>
          Best suited for a <strong>{prediction.architecture}</strong> architecture
          at {Math.round(prediction.confidence * 100)}% confidence. Recommended stack:{' '}
          {architecture.tech_stack.backend.join(' + ')} with{' '}
          {architecture.tech_stack.database.join(' + ')}.
        </p>
        <div className={styles.meta}>
          <span>{report.id}</span>
          <span>{new Date(report.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.downloadButton} onClick={handleDownload} disabled={downloading}>
          {downloading ? 'Preparing PDF' : 'Download PDF report'}
        </button>
        {downloadError && <span className={styles.downloadError}>{downloadError}</span>}

        <button className={styles.restartButton} onClick={onRestart}>
          New analysis
        </button>
      </div>
    </div>
  )
}
