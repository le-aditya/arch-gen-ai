import { useState } from 'react'
import styles from './Screen1Input.module.css'

export default function Screen1Input({ onAnalyze, loading, error }) {
  const [form, setForm] = useState({
    description: '',
    team_size: 2,
    budget: 'low',
    expected_users: 'low',
    availability: 'medium'
  })
  const [submitted, setSubmitted] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const isValid = form.description.trim().length > 0

  const handleSubmit = (e) => {
    e.preventDefault()
    setSubmitted(true)
    if (!isValid) return
    onAnalyze(form)
  }

  return (
    <div className={styles.container}>
      <div className={styles.mark}>Arch Gen AI</div>

      <h1 className={styles.headline}>
        Design the architecture
        <br />
        before you write the code.
      </h1>
      <p className={styles.subhead}>
        Describe the system. We'll map its requirements, constraints, and architecture.
      </p>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.field}>
          <div className={styles.fieldHead}>
            <label className={styles.fieldLabel} htmlFor="description">
              Application description
            </label>
            <span className={styles.charCount}>{form.description.length} chars</span>
          </div>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="I want to build an online food delivery platform where customers can browse restaurants, order food, make payments and track delivery..."
            required
          />
          {submitted && !isValid && (
            <span className={styles.fieldHint}>Please provide an application description.</span>
          )}
        </div>

        <div className={styles.row}>
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="team_size">
              Team size
            </label>
            <select id="team_size" name="team_size" value={form.team_size} onChange={handleChange}>
              <option value={1}>1 person</option>
              <option value={2}>2 people</option>
              <option value={3}>3 people</option>
              <option value={4}>4 people</option>
              <option value={5}>5 people</option>
              <option value={6}>6+ people</option>
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="budget">
              Budget
            </label>
            <select id="budget" name="budget" value={form.budget} onChange={handleChange}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="expected_users">
              Expected users
            </label>
            <select id="expected_users" name="expected_users" value={form.expected_users} onChange={handleChange}>
              <option value="low">Low (&lt;1K)</option>
              <option value="medium">Medium (1K–100K)</option>
              <option value="high">High (100K+)</option>
            </select>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.fieldLabel} htmlFor="availability">
            Availability requirement
          </label>
          <select id="availability" name="availability" value={form.availability} onChange={handleChange}>
            <option value="low">Low — downtime is acceptable</option>
            <option value="medium">Medium — some downtime OK</option>
            <option value="high">High — must be always available</option>
          </select>
        </div>

        {error && <span className={styles.formError}>{error}</span>}

        <button type="submit" className={styles.analyzeButton} disabled={loading}>
          {loading ? 'Analyzing' : (
            <>
              Analyze <span aria-hidden="true">→</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}
