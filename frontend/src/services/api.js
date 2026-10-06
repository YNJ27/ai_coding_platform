const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!response.ok) {
    throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`)
  }
  return response.json()
}

export function fetchProblems() {
  return request('/problems')
}

export function fetchProblem(problemId) {
  return request(`/problems/${problemId}`)
}

export function getOrCreateUserId() {
  const storageKey = 'coding-platform-user-id'
  const existingUserId = localStorage.getItem(storageKey)
  if (existingUserId) return existingUserId
  const userId = crypto.randomUUID()
  localStorage.setItem(storageKey, userId)
  return userId
}

export function saveSessionFile({ sessionId, path, content }) {
  return request(`/sessions/${sessionId}/files`, {
    method: 'PUT',
    body: JSON.stringify({ path, content }),
  })
}

export function createCodingSession({ userId, problemId }) {
  return request('/sessions', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, problem_id: problemId }),
  })
}

export function fetchSessionFiles(sessionId) {
  return request(`/sessions/${sessionId}/files`)
}

export function runCodingSession(sessionId) {
  return request(`/sessions/${sessionId}/run`, { method: 'POST' })
}

export function fetchChatHistory(sessionId) {
  return request(`/sessions/${sessionId}/chat`)
}

export function sendChatMessage({ sessionId, message }) {
  return request(`/sessions/${sessionId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}
