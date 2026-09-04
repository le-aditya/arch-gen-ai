import { useState } from 'react'
import PipelineNav from './components/PipelineNav/PipelineNav'
import Screen1Input from './components/Screen1Input/Screen1Input'
import Screen2Requirements from './components/Screen2Requirements/Screen2Requirements'
import Screen3Prediction from './components/Screen3Prediction/Screen3Prediction'
import Screen4Architecture from './components/Screen4Architecture/Screen4Architecture'
import Screen5Report from './components/Screen5Report/Screen5Report'
import { analyze } from './services/api'
import styles from './App.module.css'

function App() {
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleAnalyze = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const data = await analyze(formData)
      setResult(data)
      setCurrentStep(1)
    } catch (err) {
      setError(err.message || 'Unable to analyze this project. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRestart = () => {
    setResult(null)
    setError(null)
    setCurrentStep(0)
  }

  return (
    <div className={styles.app}>
      <PipelineNav currentStep={currentStep} onStepClick={result ? setCurrentStep : () => {}} />
      <main className={styles.main}>
        {currentStep === 0 && (
          <Screen1Input onAnalyze={handleAnalyze} loading={loading} error={error} />
        )}
        {currentStep === 1 && result && (
          <Screen2Requirements
            requirements={result.requirements}
            onNext={() => setCurrentStep(2)}
          />
        )}
        {currentStep === 2 && result && (
          <Screen3Prediction
            prediction={result.prediction}
            onNext={() => setCurrentStep(3)}
          />
        )}
        {currentStep === 3 && result && (
          <Screen4Architecture
            architecture={{
              tech_stack: result.tech_stack,
              database: result.database,
              apis: result.apis,
              diagrams: result.diagrams,
            }}
            onNext={() => setCurrentStep(4)}
          />
        )}
        {currentStep === 4 && result && (
          <Screen5Report
            report={{ id: result.report_id, created_at: result.created_at }}
            prediction={result.prediction}
            architecture={{
              tech_stack: result.tech_stack,
              database: result.database,
              apis: result.apis,
              diagrams: result.diagrams,
            }}
            onRestart={handleRestart}
          />
        )}
      </main>
    </div>
  )
}

export default App
