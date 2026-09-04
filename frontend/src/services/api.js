const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function handleResponse(response) {
  if (!response.ok) {
    let detail = 'Something went wrong. Please try again.'
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — keep the default message
    }
    throw new Error(detail)
  }
  return response.json()
}

export async function analyze(formData) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      description: formData.description,
      team_size: Number(formData.team_size),
      budget: formData.budget,
      expected_users: formData.expected_users,
      availability: formData.availability,
    }),
  })
  return handleResponse(response)
}

export async function downloadReport(reportId) {
  const response = await fetch(`${BASE_URL}/report/${reportId}`)
  if (!response.ok) {
    throw new Error('Unable to download the report. Please try again.')
  }
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${reportId}.pdf`
  link.click()
  URL.revokeObjectURL(url)
}
