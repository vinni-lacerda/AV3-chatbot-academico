const base = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')

export async function request(path, { token, signal, method = 'GET', body } = {}) {
  const headers = { Accept: 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    response = await fetch(`${base}${path}`, {
      headers, method, signal, body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Não foi possível conectar à API. Confira a conexão e tente novamente.')
  }
  const result = await response.json().catch(() => null)
  if (!response.ok || result === null) {
    const error = new Error(result?.detail || 'A API não conseguiu concluir a solicitação. Tente novamente.')
    error.status = response.status
    throw error
  }
  return result
}
