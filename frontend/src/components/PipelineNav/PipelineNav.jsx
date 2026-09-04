import styles from './PipelineNav.module.css'

const steps = [
  { label: 'Describe', number: '01' },
  { label: 'Extract', number: '02' },
  { label: 'Predict', number: '03' },
  { label: 'Generate', number: '04' },
  { label: 'Report', number: '05' },
]

export default function PipelineNav({ currentStep, onStepClick }) {
  return (
    <nav className={styles.pipeline} aria-label="Analysis pipeline">
      <div className={styles.rail}>
        {steps.map((step, index) => {
          const isActive = index === currentStep
          const isDone = index < currentStep

          return (
            <div className={styles.segment} key={step.label}>
              <button
                className={styles.step}
                data-state={isActive ? 'active' : isDone ? 'done' : 'pending'}
                onClick={() => onStepClick(index)}
                aria-current={isActive ? 'step' : undefined}
              >
                <span className={styles.stepNumber}>{step.number}</span>
                <span className={styles.stepLabel}>{step.label}</span>
              </button>
              {index < steps.length - 1 && (
                <div className={styles.connector} data-filled={isDone} aria-hidden="true" />
              )}
            </div>
          )
        })}
      </div>
    </nav>
  )
}
