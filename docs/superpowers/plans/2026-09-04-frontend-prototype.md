# ARCH GEN AI Frontend Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 5-screen React prototype with mock data, pipeline navigation, and the blueprint design language.

**Architecture:** Vite + React (JS) + CSS Modules. No routing library — simple state-based screen switching. All data is mock/static. The prototype validates the visual design and user flow before any backend integration.

**Tech Stack:** Vite 5, React 18, CSS Modules, JavaScript (no TypeScript)

**Spec:** `docs/superpowers/specs/2026-09-04-frontend-prototype-design.md`

## Global Constraints

- No TypeScript — plain JavaScript only
- No routing library — state-based screen switching
- No external UI component libraries (no MUI, no Ant Design)
- CSS Modules for scoped styling — no Tailwind, no Styled Components
- Blueprint color palette: Blueprint Ink `#0E2A3F`, Drafting Paper `#FAFAF7`, Cyanotype Line `#3E7CB1`, Signal Amber `#D98E36`, Graphite `#5C6670`
- No purple gradients, no glassmorphism, no decorative elements
- All data is mock — no API calls
- Mobile-responsive not required for prototype (desktop-first)

---

## File Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx                    # Entry point, renders App
│   ├── App.jsx                     # Root component, screen state
│   ├── App.module.css              # Global layout styles
│   ├── index.css                   # CSS reset and variables
│   ├── components/
│   │   ├── PipelineNav/
│   │   │   ├── PipelineNav.jsx     # Top pipeline step indicator
│   │   │   └── PipelineNav.module.css
│   │   ├── Screen1Input/
│   │   │   ├── Screen1Input.jsx    # Project input form
│   │   │   └── Screen1Input.module.css
│   │   ├── Screen2Requirements/
│   │   │   ├── Screen2Requirements.jsx  # Extracted requirements display
│   │   │   └── Screen2Requirements.module.css
│   │   ├── Screen3Prediction/
│   │   │   ├── Screen3Prediction.jsx    # Architecture prediction + confidence
│   │   │   └── Screen3Prediction.module.css
│   │   ├── Screen4Architecture/
│   │   │   ├── Screen4Architecture.jsx  # Generated architecture artifacts
│   │   │   └── Screen4Architecture.module.css
│   │   └── Screen5Report/
│   │       ├── Screen5Report.jsx        # Report summary + download
│   │       └── Screen5Report.module.css
│   └── data/
│       └── mockData.js            # All mock data for all screens
```

---

## Task 1: Scaffold Vite Project

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/App.module.css`
- Create: `frontend/src/index.css`

**Interfaces:**
- Consumes: Nothing (first task)
- Produces: Running Vite dev server with empty React app

- [ ] **Step 1: Create package.json**

```json
{
  "name": "arch-gen-ai-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

- [ ] **Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ARCH GEN AI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Create src/index.css with CSS variables**

```css
:root {
  /* Blueprint Palette */
  --blueprint-ink: #0E2A3F;
  --drafting-paper: #FAFAF7;
  --cyanotype-line: #3E7CB1;
  --signal-amber: #D98E36;
  --graphite: #5C6670;

  /* Derived */
  --border-color: #3E7CB133;
  --card-bg: #FAFAF7;
  --text-primary: #0E2A3F;
  --text-secondary: #5C6670;
  --font-mono: 'Courier New', Courier, monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  background-color: var(--drafting-paper);
  color: var(--text-primary);
  min-height: 100vh;
}
```

- [ ] **Step 5: Create src/main.jsx**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 6: Create src/App.jsx (placeholder)**

```jsx
import styles from './App.module.css'

function App() {
  return (
    <div className={styles.app}>
      <h1>ARCH GEN AI</h1>
      <p>Prototype loading...</p>
    </div>
  )
}

export default App
```

- [ ] **Step 7: Create src/App.module.css**

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.app h1 {
  font-family: var(--font-mono);
  color: var(--blueprint-ink);
  font-size: 2rem;
  letter-spacing: 0.1em;
}
```

- [ ] **Step 8: Install dependencies and verify**

Run:
```bash
cd frontend && npm install && npm run dev
```
Expected: Dev server starts on port 5173, browser shows "ARCH GEN AI"

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vite + React project with blueprint CSS variables"
```

---

## Task 2: Create Mock Data

**Files:**
- Create: `frontend/src/data/mockData.js`

**Interfaces:**
- Consumes: Nothing
- Produces: Exported objects consumed by all screen components

- [ ] **Step 1: Create mockData.js**

```javascript
export const mockInput = {
  description: "I want to build an online food delivery platform where customers can browse restaurants, order food, make payments and track delivery in real-time.",
  team_size: 4,
  budget: "low",
  expected_users: "medium",
  availability: "high"
}

export const mockRequirements = {
  domain: "food_delivery",
  actors: ["customer", "restaurant", "delivery_partner", "admin"],
  modules: [
    "registration",
    "restaurant_browsing",
    "ordering",
    "payment",
    "tracking",
    "notifications"
  ],
  real_time: true,
  payment: true,
  external_integrations: ["maps", "payment_gateway", "sms"],
  data_complexity: "high"
}

export const mockPrediction = {
  architecture: "Microservices",
  confidence: 0.84,
  top_factors: [
    { name: "Real-time requirement", importance: 0.28 },
    { name: "Number of modules", importance: 0.22 },
    { name: "External integrations", importance: 0.18 },
    { name: "Availability requirement", importance: 0.15 },
    { name: "Data complexity", importance: 0.12 }
  ]
}

export const mockArchitecture = {
  tech_stack: {
    frontend: ["React", "TypeScript"],
    backend: ["Node.js", "Express"],
    database: ["PostgreSQL", "Redis"],
    messaging: ["RabbitMQ"],
    infrastructure: ["Docker", "Nginx"]
  },
  database: {
    tables: [
      {
        name: "Customer",
        columns: ["customer_id PK", "name", "email", "phone", "created_at"]
      },
      {
        name: "Restaurant",
        columns: ["restaurant_id PK", "name", "cuisine_type", "address", "is_active"]
      },
      {
        name: "Order",
        columns: ["order_id PK", "customer_id FK", "restaurant_id FK", "status", "total", "created_at"]
      },
      {
        name: "Payment",
        columns: ["payment_id PK", "order_id FK", "amount", "method", "status", "paid_at"]
      }
    ]
  },
  apis: [
    { method: "POST", path: "/api/auth/register", purpose: "Register new user" },
    { method: "POST", path: "/api/auth/login", purpose: "User login" },
    { method: "GET", path: "/api/restaurants", purpose: "List restaurants" },
    { method: "POST", path: "/api/orders", purpose: "Create new order" },
    { method: "GET", path: "/api/orders/:id/track", purpose: "Track order" },
    { method: "POST", path: "/api/payments", purpose: "Process payment" }
  ],
  diagrams: {
    architecture: "Microservices with API Gateway",
    deployment: "Load Balancer → Docker Containers → PostgreSQL + Redis"
  }
}

export const mockReport = {
  id: "rpt_001",
  created_at: "2026-09-04T10:30:00Z",
  summary: "Food delivery platform recommended for microservices architecture with 84% confidence."
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/data/mockData.js
git commit -m "feat: add mock data for all 5 prototype screens"
```

---

## Task 3: Build PipelineNav Component

**Files:**
- Create: `frontend/src/components/PipelineNav/PipelineNav.jsx`
- Create: `frontend/src/components/PipelineNav/PipelineNav.module.css`
- Modify: `frontend/src/App.jsx` (import and render PipelineNav)

**Interfaces:**
- Consumes: `currentStep` (number 0-4), `onStepClick` (function)
- Produces: Renders pipeline step indicator bar

- [ ] **Step 1: Create PipelineNav.module.css**

```css
.pipeline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 1.5rem 2rem;
  background: var(--blueprint-ink);
  border-bottom: 2px solid var(--cyanotype-line);
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stepNumber {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--graphite);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--graphite);
  transition: all 0.2s ease;
}

.stepLabel {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  color: var(--graphite);
  text-transform: uppercase;
}

.step.active .stepNumber {
  background: var(--cyanotype-line);
  border-color: var(--cyanotype-line);
  color: white;
}

.step.active .stepLabel {
  color: var(--cyanotype-line);
}

.step.completed .stepNumber {
  background: var(--signal-amber);
  border-color: var(--signal-amber);
  color: white;
}

.step.completed .stepLabel {
  color: var(--signal-amber);
}

.connector {
  width: 40px;
  height: 2px;
  background: var(--graphite);
  opacity: 0.3;
}

.connector.active {
  background: var(--cyanotype-line);
  opacity: 1;
}
```

- [ ] **Step 2: Create PipelineNav.jsx**

```jsx
import styles from './PipelineNav.module.css'

const steps = [
  { label: 'Describe', number: 1 },
  { label: 'Extract', number: 2 },
  { label: 'Predict', number: 3 },
  { label: 'Generate', number: 4 },
]

export default function PipelineNav({ currentStep, onStepClick }) {
  return (
    <nav className={styles.pipeline}>
      {steps.map((step, index) => (
        <div key={step.label} style={{ display: 'flex', alignItems: 'center' }}>
          <div
            className={`${styles.step} ${
              index === currentStep ? styles.active : ''
            } ${index < currentStep ? styles.completed : ''}`}
            onClick={() => onStepClick(index)}
          >
            <div className={styles.stepNumber}>{step.number}</div>
            <span className={styles.stepLabel}>{step.label}</span>
          </div>
          {index < steps.length - 1 && (
            <div
              className={`${styles.connector} ${
                index < currentStep ? styles.active : ''
              }`}
            />
          )}
        </div>
      ))}
    </nav>
  )
}
```

- [ ] **Step 3: Update App.jsx to use PipelineNav**

```jsx
import { useState } from 'react'
import PipelineNav from './components/PipelineNav/PipelineNav'
import styles from './App.module.css'

function App() {
  const [currentStep, setCurrentStep] = useState(0)

  return (
    <div className={styles.app}>
      <PipelineNav currentStep={currentStep} onStepClick={setCurrentStep} />
      <main className={styles.main}>
        <p>Screen placeholder — step {currentStep + 1}</p>
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 4: Update App.module.css**

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
```

- [ ] **Step 5: Verify in browser**

Run: `npm run dev`
Expected: Pipeline bar at top with 4 steps, clicking steps highlights them

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/PipelineNav/ frontend/src/App.jsx frontend/src/App.module.css
git commit -m "feat: add PipelineNav component with step indicator"
```

---

## Task 4: Build Screen1 — Project Input

**Files:**
- Create: `frontend/src/components/Screen1Input/Screen1Input.jsx`
- Create: `frontend/src/components/Screen1Input/Screen1Input.module.css`
- Modify: `frontend/src/App.jsx` (conditional render)

**Interfaces:**
- Consumes: `onAnalyze` (function called with form data)
- Produces: Form with description textarea, team size, budget, expected users, availability

- [ ] **Step 1: Create Screen1Input.module.css**

```css
.container {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  color: var(--blueprint-ink);
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--cyanotype-line);
  padding-bottom: 0.5rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}

.field textarea {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
  color: var(--text-primary);
  resize: vertical;
  min-height: 120px;
}

.field textarea:focus {
  outline: none;
  border-color: var(--cyanotype-line);
  box-shadow: 0 0 0 2px rgba(62, 124, 177, 0.15);
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.field select {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
  color: var(--text-primary);
  cursor: pointer;
}

.field select:focus {
  outline: none;
  border-color: var(--cyanotype-line);
}

.button {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.85rem 2rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  align-self: flex-start;
}

.button:hover {
  background: var(--cyanotype-line);
}
```

- [ ] **Step 2: Create Screen1Input.jsx**

```jsx
import { useState } from 'react'
import styles from './Screen1Input.module.css'

export default function Screen1Input({ onAnalyze }) {
  const [form, setForm] = useState({
    description: '',
    team_size: 2,
    budget: 'low',
    expected_users: 'low',
    availability: 'medium'
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onAnalyze(form)
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Describe Your Application</h2>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.field}>
          <label>Application Description</label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="I want to build an online food delivery platform..."
          />
        </div>
        <div className={styles.row}>
          <div className={styles.field}>
            <label>Team Size</label>
            <select name="team_size" value={form.team_size} onChange={handleChange}>
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
              <option value={4}>4</option>
              <option value={5}>5</option>
              <option value={6}>6+</option>
            </select>
          </div>
          <div className={styles.field}>
            <label>Budget</label>
            <select name="budget" value={form.budget} onChange={handleChange}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div className={styles.field}>
            <label>Expected Users</label>
            <select name="expected_users" value={form.expected_users} onChange={handleChange}>
              <option value="low">Low (&lt;1K)</option>
              <option value="medium">Medium (1K-100K)</option>
              <option value="high">High (100K+)</option>
            </select>
          </div>
        </div>
        <div className={styles.field}>
          <label>Availability Requirement</label>
          <select name="availability" value={form.availability} onChange={handleChange}>
            <option value="low">Low — Downtime acceptable</option>
            <option value="medium">Medium — Some downtime OK</option>
            <option value="high">High — Must be always available</option>
          </select>
        </div>
        <button type="submit" className={styles.button}>Analyze</button>
      </form>
    </div>
  )
}
```

- [ ] **Step 3: Update App.jsx to render Screen1**

```jsx
import { useState } from 'react'
import PipelineNav from './components/PipelineNav/PipelineNav'
import Screen1Input from './components/Screen1Input/Screen1Input'
import { mockRequirements, mockPrediction, mockArchitecture, mockReport } from './data/mockData'
import styles from './App.module.css'

function App() {
  const [currentStep, setCurrentStep] = useState(0)

  const handleAnalyze = (formData) => {
    setCurrentStep(1)
  }

  return (
    <div className={styles.app}>
      <PipelineNav currentStep={currentStep} onStepClick={setCurrentStep} />
      <main className={styles.main}>
        {currentStep === 0 && <Screen1Input onAnalyze={handleAnalyze} />}
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 4: Verify in browser**

Expected: Form renders with all fields, clicking Analyze advances pipeline to step 2

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Screen1Input/ frontend/src/App.jsx
git commit -m "feat: add Screen1 project input form"
```

---

## Task 5: Build Screen2 — Requirements Display

**Files:**
- Create: `frontend/src/components/Screen2Requirements/Screen2Requirements.jsx`
- Create: `frontend/src/components/Screen2Requirements/Screen2Requirements.module.css`
- Modify: `frontend/src/App.jsx` (add conditional render)

**Interfaces:**
- Consumes: `requirements` object, `onNext` (function)
- Produces: Displays domain, actors, modules, real-time, payment, integrations, data complexity

- [ ] **Step 1: Create Screen2Requirements.module.css**

```css
.container {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  color: var(--blueprint-ink);
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--cyanotype-line);
  padding-bottom: 0.5rem;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sectionLabel {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  border-radius: 3px;
}

.boolean {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.booleanDot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.booleanDot.yes {
  background: var(--cyanotype-line);
}

.booleanDot.no {
  background: var(--graphite);
}

.domain {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  color: var(--blueprint-ink);
  text-transform: capitalize;
}

.button {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.85rem 2rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  align-self: flex-start;
}

.button:hover {
  background: var(--cyanotype-line);
}
```

- [ ] **Step 2: Create Screen2Requirements.jsx**

```jsx
import styles from './Screen2Requirements.module.css'

export default function Screen2Requirements({ requirements, onNext }) {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Extracted Requirements</h2>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Domain</span>
        <span className={styles.domain}>{requirements.domain}</span>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Actors</span>
        <div className={styles.tags}>
          {requirements.actors.map(actor => (
            <span key={actor} className={styles.tag}>{actor}</span>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Modules</span>
        <div className={styles.tags}>
          {requirements.modules.map(mod => (
            <span key={mod} className={styles.tag}>{mod}</span>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Capabilities</span>
        <div className={styles.boolean}>
          <span className={`${styles.booleanDot} ${requirements.real_time ? styles.yes : styles.no}`} />
          Real-time: {requirements.real_time ? 'Yes' : 'No'}
        </div>
        <div className={styles.boolean}>
          <span className={`${styles.booleanDot} ${requirements.payment ? styles.yes : styles.no}`} />
          Payment: {requirements.payment ? 'Yes' : 'No'}
        </div>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>External Integrations</span>
        <div className={styles.tags}>
          {requirements.external_integrations.map(int => (
            <span key={int} className={styles.tag}>{int}</span>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Data Complexity</span>
        <span className={styles.domain}>{requirements.data_complexity}</span>
      </div>

      <button className={styles.button} onClick={onNext}>
        Predict Architecture
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Update App.jsx to handle steps 0-1**

```jsx
import { useState } from 'react'
import PipelineNav from './components/PipelineNav/PipelineNav'
import Screen1Input from './components/Screen1Input/Screen1Input'
import Screen2Requirements from './components/Screen2Requirements/Screen2Requirements'
import { mockRequirements, mockPrediction, mockArchitecture, mockReport } from './data/mockData'
import styles from './App.module.css'

function App() {
  const [currentStep, setCurrentStep] = useState(0)

  const handleAnalyze = (formData) => {
    setCurrentStep(1)
  }

  return (
    <div className={styles.app}>
      <PipelineNav currentStep={currentStep} onStepClick={setCurrentStep} />
      <main className={styles.main}>
        {currentStep === 0 && <Screen1Input onAnalyze={handleAnalyze} />}
        {currentStep === 1 && (
          <Screen2Requirements
            requirements={mockRequirements}
            onNext={() => setCurrentStep(2)}
          />
        )}
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 4: Verify in browser**

Expected: Fill form, click Analyze → see requirements with domain, actors, modules, booleans, integrations

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Screen2Requirements/ frontend/src/App.jsx
git commit -m "feat: add Screen2 requirements display"
```

---

## Task 6: Build Screen3 — Architecture Prediction

**Files:**
- Create: `frontend/src/components/Screen3Prediction/Screen3Prediction.jsx`
- Create: `frontend/src/components/Screen3Prediction/Screen3Prediction.module.css`
- Modify: `frontend/src/App.jsx` (add conditional render)

**Interfaces:**
- Consumes: `prediction` object (architecture, confidence, top_factors), `onNext` (function)
- Produces: Architecture name, confidence bar, feature importance bars

- [ ] **Step 1: Create Screen3Prediction.module.css**

```css
.container {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  color: var(--blueprint-ink);
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--cyanotype-line);
  padding-bottom: 0.5rem;
}

.archName {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: bold;
  color: var(--blueprint-ink);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.confidenceSection {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.confidenceLabel {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
}

.confidenceBar {
  width: 100%;
  height: 32px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.confidenceFill {
  height: 100%;
  background: var(--cyanotype-line);
  transition: width 0.6s ease;
}

.confidenceText {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: bold;
  color: var(--blueprint-ink);
}

.factors {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.factorsTitle {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
}

.factor {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.factorName {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-primary);
}

.factorBar {
  width: 100%;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.factorFill {
  height: 100%;
  background: var(--signal-amber);
  border-radius: 4px;
}

.button {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.85rem 2rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  align-self: flex-start;
}

.button:hover {
  background: var(--cyanotype-line);
}
```

- [ ] **Step 2: Create Screen3Prediction.jsx**

```jsx
import styles from './Screen3Prediction.module.css'

export default function Screen3Prediction({ prediction, onNext }) {
  const maxImportance = Math.max(...prediction.top_factors.map(f => f.importance))

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Architecture Prediction</h2>

      <div className={styles.archName}>{prediction.architecture}</div>

      <div className={styles.confidenceSection}>
        <span className={styles.confidenceLabel}>Confidence</span>
        <div className={styles.confidenceBar}>
          <div
            className={styles.confidenceFill}
            style={{ width: `${prediction.confidence * 100}%` }}
          />
          <span className={styles.confidenceText}>
            {Math.round(prediction.confidence * 100)}%
          </span>
        </div>
      </div>

      <div className={styles.factors}>
        <span className={styles.factorsTitle}>Important Factors</span>
        {prediction.top_factors.map(factor => (
          <div key={factor.name} className={styles.factor}>
            <span className={styles.factorName}>{factor.name}</span>
            <div className={styles.factorBar}>
              <div
                className={styles.factorFill}
                style={{ width: `${(factor.importance / maxImportance) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <button className={styles.button} onClick={onNext}>
        Generate Architecture
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Update App.jsx to handle steps 0-2**

Add Screen3Prediction import and conditional render for `currentStep === 2`.

- [ ] **Step 4: Verify in browser**

Expected: See "MICROSERVICES" in large text, confidence bar at 84%, factor bars with amber fill

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Screen3Prediction/ frontend/src/App.jsx
git commit -m "feat: add Screen3 architecture prediction with confidence and factors"
```

---

## Task 7: Build Screen4 — Generated Architecture

**Files:**
- Create: `frontend/src/components/Screen4Architecture/Screen4Architecture.jsx`
- Create: `frontend/src/components/Screen4Architecture/Screen4Architecture.module.css`
- Modify: `frontend/src/App.jsx` (add conditional render)

**Interfaces:**
- Consumes: `architecture` object (tech_stack, database, apis, diagrams), `onNext` (function)
- Produces: Tech stack grid, DB schema, API list, diagram descriptions

- [ ] **Step 1: Create Screen4Architecture.module.css**

```css
.container {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  color: var(--blueprint-ink);
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--cyanotype-line);
  padding-bottom: 0.5rem;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sectionLabel {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
}

.techGrid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.techCard {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
}

.techCategory {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--cyanotype-line);
  margin-bottom: 0.3rem;
}

.techItems {
  font-family: var(--font-sans);
  font-size: 0.85rem;
  color: var(--text-primary);
}

.dbTable {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.dbTable th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dbTable td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.apiList {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.apiItem {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
}

.method {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: bold;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  min-width: 50px;
  text-align: center;
}

.method.GET { background: var(--cyanotype-line); color: white; }
.method.POST { background: var(--signal-amber); color: white; }
.method.PUT { background: var(--graphite); color: white; }
.method.DELETE { background: #c0392b; color: white; }

.apiPath {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-primary);
}

.apiPurpose {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-left: auto;
}

.button {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.85rem 2rem;
  background: var(--blueprint-ink);
  color: var(--drafting-paper);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  align-self: flex-start;
}

.button:hover {
  background: var(--cyanotype-line);
}
```

- [ ] **Step 2: Create Screen4Architecture.jsx**

```jsx
import styles from './Screen4Architecture.module.css'

export default function Screen4Architecture({ architecture, onNext }) {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Generated Architecture</h2>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Technology Stack</span>
        <div className={styles.techGrid}>
          {Object.entries(architecture.tech_stack).map(([category, items]) => (
            <div key={category} className={styles.techCard}>
              <div className={styles.techCategory}>{category}</div>
              <div className={styles.techItems}>{items.join(' + ')}</div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>Database Schema</span>
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
                <td>{table.name}</td>
                <td>{table.columns.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className={styles.section}>
        <span className={styles.sectionLabel}>API Endpoints</span>
        <div className={styles.apiList}>
          {architecture.apis.map((api, i) => (
            <div key={i} className={styles.apiItem}>
              <span className={`${styles.method} ${styles[api.method]}`}>{api.method}</span>
              <span className={styles.apiPath}>{api.path}</span>
              <span className={styles.apiPurpose}>{api.purpose}</span>
            </div>
          ))}
        </div>
      </div>

      <button className={styles.button} onClick={onNext}>
        View Report
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Update App.jsx to handle steps 0-3**

- [ ] **Step 4: Verify in browser**

Expected: Tech stack grid, DB schema table, API list with colored method badges

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Screen4Architecture/ frontend/src/App.jsx
git commit -m "feat: add Screen4 generated architecture display"
```

---

## Task 8: Build Screen5 — Report

**Files:**
- Create: `frontend/src/components/Screen5Report/Screen5Report.jsx`
- Create: `frontend/src/components/Screen5Report/Screen5Report.module.css`
- Modify: `frontend/src/App.jsx` (add conditional render)

**Interfaces:**
- Consumes: `report` object, `prediction` object, `architecture` object
- Produces: Summary view with download button

- [ ] **Step 1: Create Screen5Report.module.css**

```css
.container {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.title {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  color: var(--blueprint-ink);
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--cyanotype-line);
  padding-bottom: 0.5rem;
}

.summaryCard {
  padding: 1.5rem;
  border: 2px solid var(--cyanotype-line);
  border-radius: 4px;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summaryTitle {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  color: var(--blueprint-ink);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summaryText {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-primary);
}

.summaryMeta {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
  display: flex;
  gap: 1.5rem;
}

.downloadButton {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.85rem 2rem;
  background: var(--signal-amber);
  color: var(--blueprint-ink);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
  align-self: flex-start;
}

.downloadButton:hover {
  background: var(--cyanotype-line);
  color: var(--drafting-paper);
}

.restartButton {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  padding: 0.6rem 1.5rem;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  align-self: flex-start;
}

.restartButton:hover {
  border-color: var(--cyanotype-line);
  color: var(--cyanotype-line);
}
```

- [ ] **Step 2: Create Screen5Report.jsx**

```jsx
import styles from './Screen5Report.module.css'

export default function Screen5Report({ report, prediction, architecture, onRestart }) {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Report</h2>

      <div className={styles.summaryCard}>
        <span className={styles.summaryTitle}>Architecture Recommendation</span>
        <p className={styles.summaryText}>
          Your application is best suited for a <strong>{prediction.architecture}</strong> architecture
          with {Math.round(prediction.confidence * 100)}% confidence. The recommended stack includes{' '}
          {architecture.tech_stack.backend.join(' and ')} backend with{' '}
          {architecture.tech_stack.database.join(' and ')} database.
        </p>
        <div className={styles.summaryMeta}>
          <span>Report ID: {report.id}</span>
          <span>Generated: {new Date(report.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      <button className={styles.downloadButton}>
        Download PDF Report
      </button>

      <button className={styles.restartButton} onClick={onRestart}>
        Start New Analysis
      </button>
    </div>
  )
}
```

- [ ] **Step 3: Update App.jsx to handle all 5 steps**

```jsx
import { useState } from 'react'
import PipelineNav from './components/PipelineNav/PipelineNav'
import Screen1Input from './components/Screen1Input/Screen1Input'
import Screen2Requirements from './components/Screen2Requirements/Screen2Requirements'
import Screen3Prediction from './components/Screen3Prediction/Screen3Prediction'
import Screen4Architecture from './components/Screen4Architecture/Screen4Architecture'
import Screen5Report from './components/Screen5Report/Screen5Report'
import { mockRequirements, mockPrediction, mockArchitecture, mockReport } from './data/mockData'
import styles from './App.module.css'

function App() {
  const [currentStep, setCurrentStep] = useState(0)

  const handleAnalyze = (formData) => {
    setCurrentStep(1)
  }

  const handleRestart = () => {
    setCurrentStep(0)
  }

  return (
    <div className={styles.app}>
      <PipelineNav currentStep={currentStep} onStepClick={setCurrentStep} />
      <main className={styles.main}>
        {currentStep === 0 && <Screen1Input onAnalyze={handleAnalyze} />}
        {currentStep === 1 && (
          <Screen2Requirements
            requirements={mockRequirements}
            onNext={() => setCurrentStep(2)}
          />
        )}
        {currentStep === 2 && (
          <Screen3Prediction
            prediction={mockPrediction}
            onNext={() => setCurrentStep(3)}
          />
        )}
        {currentStep === 3 && (
          <Screen4Architecture
            architecture={mockArchitecture}
            onNext={() => setCurrentStep(4)}
          />
        )}
        {currentStep === 4 && (
          <Screen5Report
            report={mockReport}
            prediction={mockPrediction}
            architecture={mockArchitecture}
            onRestart={handleRestart}
          />
        )}
      </main>
    </div>
  )
}

export default App
```

- [ ] **Step 4: Verify full flow**

Expected: Complete walkthrough — form → requirements → prediction → architecture → report → restart

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Screen5Report/ frontend/src/App.jsx
git commit -m "feat: add Screen5 report and complete 5-screen prototype flow"
```

---

## Task 9: Final Polish and Build

**Files:**
- Modify: `frontend/src/index.css` (minor tweaks if needed)
- Verify: All components render correctly

**Interfaces:**
- Consumes: All previous tasks
- Produces: Working prototype ready for demo

- [ ] **Step 1: Run full visual check**

Run: `npm run dev`
Walk through all 5 screens, check:
- PipelineNav highlights correctly
- All text is readable
- Colors match blueprint palette
- No layout breaks

- [ ] **Step 2: Run production build**

Run: `npm run build`
Expected: No errors, dist/ folder created

- [ ] **Step 3: Commit final state**

```bash
git add .
git commit -m "feat: complete frontend prototype with blueprint design"
```

---

## Summary

| Task | Deliverable | Est. Time |
|------|-------------|-----------|
| 1 | Vite scaffold + CSS variables | 10 min |
| 2 | Mock data | 5 min |
| 3 | PipelineNav component | 15 min |
| 4 | Screen1 Input form | 15 min |
| 5 | Screen2 Requirements | 15 min |
| 6 | Screen3 Prediction | 15 min |
| 7 | Screen4 Architecture | 20 min |
| 8 | Screen5 Report | 15 min |
| 9 | Polish + build verification | 10 min |
| **Total** | | **~2 hours** |
