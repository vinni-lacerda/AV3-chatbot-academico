import { createRoot } from 'react-dom/client'
import { useCallback, useState } from 'react'
import { request } from './api'
import { Chat } from './pages/Chat'
import { Interview } from './pages/Interview'
import { Records } from './pages/Records'
import { Alert, Brand, Resource, roleNames, useAction, useResource } from './ui'
import './styles.css'

const sessionKey = 'passa-o-bastao.session'

function Connection() {
  const health = useResource(request, '/health')
  return <div className="connection" role="status">
    <span className={`dot ${health.error ? 'offline' : health.data ? 'online' : ''}`} />
    {health.error ? 'API indisponível' : health.data ? 'API conectada' : 'Conectando à API…'}
    {health.error && <button className="link" type="button" onClick={health.reload}>Verificar novamente</button>}
  </div>
}

function Login({ onLogin, expired }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const action = useAction()

  return <main className="login">
    <section className="login-cover">
      <Brand />
      <div className="login-intro">
        <h1>O conhecimento fica com a equipe.</h1>
        <p>Registre o que aprendeu no projeto e ajude quem vai assumir a próxima atividade.</p>
      </div>
      <span className="cover-note">Memória do projeto universitário</span>
    </section>
    <section className="login-pane">
      <Connection />
      <form className="login-form" onSubmit={event => {
        event.preventDefault()
        action.run(async () => {
          const result = await request('/auth/login', { method: 'POST', body: { email, password } })
          onLogin(result.access_token)
        })
      }}>
        <h2>Entre na sua conta</h2>
        <p>Acesse com o e-mail cadastrado no projeto.</p>
        {expired && <Alert>Sua sessão expirou. Entre novamente para continuar.</Alert>}
        <label>E-mail
          <input required type="email" autoComplete="username" value={email} onChange={event => setEmail(event.target.value)} />
        </label>
        <label>Senha
          <input required type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} />
        </label>
        <Alert>{action.problem}</Alert>
        <button disabled={action.busy}>{action.busy ? 'Entrando…' : 'Entrar'}</button>
      </form>
    </section>
  </main>
}

function Workspace({ api, logout, user }) {
  const [page, setPage] = useState('consultar')
  const [editorRequest, setEditorRequest] = useState(null)
  const activities = useResource(api, '/activities')
  const tabs = [
    ['consultar', 'Consulta', '◌'],
    ...(user.permissions.can_record_knowledge ? [['registrar', 'Registrar', '+']] : []),
    ...(user.permissions.can_review_knowledge ? [['revisar', 'Revisão', '✓']] : []),
    ['registros', 'Registros', '▤'],
  ]

  function navigate(nextPage) {
    setPage(nextPage)
    requestAnimationFrame(() => document.querySelector('.workspace-section:not([hidden]) h1')?.focus())
  }

  function edit(record) {
    setEditorRequest({ record })
    navigate('registrar')
  }

  return <div className="shell">
    <a className="skip" href="#main-content">Ir para o conteúdo</a>
    <aside className="sidebar">
      <Brand />
      <nav aria-label="Áreas do projeto">
        {tabs.map(([id, label, icon]) => <button key={id} type="button" className="nav-button"
          aria-current={page === id ? 'page' : undefined} onClick={() => navigate(id)}>
          <span aria-hidden="true">{icon}</span>{label}
        </button>)}
      </nav>
      <div className="profile">
        <div className="avatar" aria-hidden="true">{user.name.slice(0, 1)}</div>
        <div><strong>{user.name}</strong><small>{user.roles.map(role => roleNames[role]).join(' · ')}</small></div>
        <button type="button" className="logout" onClick={logout}>Sair</button>
      </div>
    </aside>
    <main id="main-content" tabIndex={-1} className="workspace">
      <Resource state={activities}>{({ items }) => <>
        <section className="workspace-section" hidden={page !== 'consultar'}>
          <Chat api={api} activities={items} />
        </section>
        {user.permissions.can_record_knowledge && <section className="workspace-section" hidden={page !== 'registrar'}>
          <Interview api={api} activities={items} editorRequest={editorRequest} />
        </section>}
        {page === 'revisar' && <section className="workspace-section">
          <Records api={api} user={user} activities={items} reloadActivities={activities.reload} mode="review" onEdit={edit} />
        </section>}
        {page === 'registros' && <section className="workspace-section">
          <Records api={api} user={user} activities={items} reloadActivities={activities.reload} mode="library" onEdit={edit} />
        </section>}
      </>}</Resource>
    </main>
  </div>
}

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem(sessionKey) || '')
  const [expired, setExpired] = useState(false)
  const api = useCallback(async (path, options) => {
    try {
      return await request(path, { ...options, token })
    } catch (error) {
      if (error.status === 401 && sessionStorage.getItem(sessionKey) === token) {
        sessionStorage.removeItem(sessionKey)
        setExpired(true)
        setToken('')
      }
      throw error
    }
  }, [token])
  const user = useResource(api, token ? '/auth/me' : null)

  if (!token) return <Login expired={expired} onLogin={value => {
    sessionStorage.setItem(sessionKey, value)
    setExpired(false)
    setToken(value)
  }} />

  function logout() {
    sessionStorage.removeItem(sessionKey)
    setToken('')
  }

  return <Resource key={token} state={user}>{profile => <Workspace api={api} user={profile} logout={logout} />}</Resource>
}

createRoot(document.getElementById('root')).render(<App />)
