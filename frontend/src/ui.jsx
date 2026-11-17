import { useEffect, useRef, useState } from 'react'

export const statusNames = {
  rascunho: 'Rascunho',
  pendente: 'Aguardando revisão',
  ajustes_solicitados: 'Ajustes solicitados',
  aprovado: 'Aprovado',
  retirado: 'Retirado',
  substituido: 'Substituído',
}

export const roleNames = {
  integrante: 'Integrante',
  novo_integrante: 'Novo integrante',
  responsavel: 'Responsável',
}

const formatter = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' })

export function dateLabel(value) {
  return formatter.format(new Date(value))
}

export function useResource(api, path) {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState({ path: null, pending: true })

  useEffect(() => {
    if (!path) return
    const controller = new AbortController()
    setResult(previous => ({
      api,
      path,
      pending: true,
      data: previous.path === path && previous.api === api ? previous.data : undefined,
    }))
    api(path, { signal: controller.signal }).then(
      data => {
        if (!controller.signal.aborted) setResult({ api, path, data, pending: false })
      },
      error => {
        if (!controller.signal.aborted) setResult({ api, path, error, pending: false })
      },
    )
    return () => controller.abort()
  }, [api, path, attempt])

  return {
    ...(result.path === path && result.api === api ? result : { pending: Boolean(path) }),
    reload: () => setAttempt(current => current + 1),
  }
}

export function useAction() {
  const lock = useRef(false)
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')

  async function run(action) {
    if (lock.current) return
    lock.current = true
    setBusy(true)
    setProblem('')
    try {
      await action()
    } catch (error) {
      setProblem(error.message)
    } finally {
      lock.current = false
      setBusy(false)
    }
  }

  return { run, busy, problem, clear: () => setProblem('') }
}

export function Alert({ children }) {
  return children ? <p className="alert" role="alert">{children}</p> : null
}

export function Resource({ state, children }) {
  if (state.error) {
    return <div className="card"><Alert>{state.error.message}</Alert>
      <button type="button" className="secondary" onClick={state.reload}>Tentar novamente</button>
    </div>
  }
  if (!state.data) return <p className="empty" role="status">Carregando…</p>
  return children(state.data)
}

export function ActivitySelect({ activities, value, onChange, caption = 'Atividade', empty = 'Todas as atividades', required = false, disabled }) {
  return <label>{caption}
    <select value={value} onChange={event => onChange(event.target.value)} required={required} disabled={disabled}>
      <option value="">{empty}</option>
      {activities.map(activity => <option key={activity.id} value={activity.id}>{activity.title}</option>)}
    </select>
  </label>
}

export function Badge({ status }) {
  return <span className={`badge ${status}`}>{statusNames[status]}</span>
}

export function PageHeader({ title, children }) {
  return <header className="page-heading"><h1 tabIndex={-1}>{title}</h1>{children && <p>{children}</p>}</header>
}

export function Brand() {
  return <div className="brand"><span className="brand-icon" aria-hidden="true">↗</span><span>Passa o Bastão</span></div>
}
