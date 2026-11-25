import { useEffect, useRef, useState } from 'react'
import { ActivitySelect, Alert, dateLabel, PageHeader, Resource, useAction, useResource } from '../ui'

function SourceContent({ api, source }) {
  const full = useResource(api, `/sources/${source.record_id}/${source.version}`)
  return <Resource state={full}>{record => {
      const content = record.versions[0].content
      return <div className="source-body">
        <p className="muted">{source.activity} · {source.author}</p>
        {record.kind === 'documento' ? <p className="preserve">{content.text}</p> : <dl className="source-content">
          {Object.entries(content).map(([key, value]) => <div key={key}>
            <dt>{{ etapas: 'Etapas', recursos: 'Recursos', dificuldades: 'Dificuldades', solucoes: 'Soluções', decisoes: 'Decisões', recomendacoes: 'Recomendações' }[key]}</dt>
            <dd className="preserve">{value}</dd>
          </div>)}
        </dl>}
      </div>
    }}</Resource>
}

function Source({ api, source }) {
  const [open, setOpen] = useState(false)
  return <details className="source" onToggle={event => setOpen(event.currentTarget.open)}>
    <summary>
      <strong>{source.title}</strong>
      <span>{source.origin} · {dateLabel(source.date)} · v{source.version}</span>
    </summary>
    {open && <SourceContent api={api} source={source} />}
  </details>
}

function Reply({ api, reply }) {
  const seen = new Set()
  const sources = reply.sources.filter(source => {
    const key = `${source.record_id}/${source.version}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })

  return <div className={`chat-reply ${reply.gap ? 'gap' : ''}`}>
    <span className="speaker">Passa o Bastão</span>
    {reply.gap && <p>{reply.answer}</p>}
    {reply.responsible && <p>Responsável de referência <strong>{reply.responsible.name}</strong></p>}
    {reply.sources.map((source, index) => <div className="excerpt" key={index}>
      <strong>{source.title}</strong>
      <p className="preserve">{source.excerpt}</p>
    </div>)}
    {sources.length > 0 && <div className="sources">
      <h3>Fontes consultadas</h3>
      {sources.map(source => <Source key={`${source.record_id}/${source.version}`} api={api} source={source} />)}
    </div>}
  </div>
}

export function Chat({ api, activities }) {
  const [turns, setTurns] = useState([])
  const [question, setQuestion] = useState('')
  const [activity, setActivity] = useState('')
  const [sending, setSending] = useState('')
  const [context, setContext] = useState('')
  const action = useAction()
  const input = useRef(null)
  const log = useRef(null)

  useEffect(() => {
    if (log.current) log.current.scrollTop = log.current.scrollHeight
  }, [turns, sending, action.problem])

  function ask(text, scope, previousActivity) {
    action.run(async () => {
      setSending(text)
      try {
        let reply = await api('/chat', {
          method: 'POST',
          body: { question: text, activity_id: scope, context_activity_id: previousActivity },
        })
        if (reply.gap && !scope && previousActivity && reply.activity_id === previousActivity) {
          const broadReply = await api('/chat', { method: 'POST', body: { question: text } })
          if (!broadReply.gap) reply = broadReply
        }
        setTurns(previous => [...previous, { text, reply, scope }])
        setContext(reply.activity_id || '')
        setQuestion('')
      } finally {
        setSending('')
        requestAnimationFrame(() => input.current?.focus())
      }
    })
  }

  function send(event) {
    event.preventDefault()
    const text = question.trim()
    if (text) ask(text, activity, context)
  }

  return <>
    <PageHeader title="Consultar conhecimento">Encontre orientações e confira as fontes aprovadas do projeto.</PageHeader>
    <div className="chat card">
      <div className="chat-toolbar">
        <ActivitySelect activities={activities} value={activity} onChange={value => {
          setActivity(value)
          setContext('')
        }} disabled={action.busy} />
        <button type="button" className="secondary" disabled={action.busy} onClick={() => {
          setTurns([])
          setQuestion('')
          setContext('')
          action.clear()
          input.current.focus()
        }}>Nova conversa</button>
      </div>
      <div className="chat-log" ref={log} role="log" aria-label="Conversa de consulta" aria-relevant="additions text">
        {turns.length === 0 && !sending && <div className="chat-empty">
          <span className="chat-mark" aria-hidden="true">↗</span>
          <h2>O que você quer saber?</h2>
          <p>Pergunte como executar uma tarefa, configurar o ambiente ou entender uma decisão da equipe.</p>
        </div>}
        {turns.map(({ text, reply, scope }, index) => <div className="chat-turn" key={index}>
          <div className="chat-question"><span className="speaker">Você</span><p className="preserve">{text}</p></div>
          <Reply api={api} reply={reply} />
          {reply.gap && scope && index === turns.length - 1 && !question.trim() &&
            <button type="button" className="secondary" disabled={action.busy} onClick={() => {
              setActivity('')
              setContext('')
              setQuestion(text)
              ask(text, '', '')
            }}>Buscar em todas as atividades</button>}
        </div>)}
        {sending && <div className="chat-turn">
          <div className="chat-question"><span className="speaker">Você</span><p className="preserve">{sending}</p></div>
          <p className="chat-reply" role="status">Buscando fontes aprovadas…</p>
        </div>}
      </div>
      <form className="composer" onSubmit={send}>
        <Alert>{action.problem}</Alert>
        <label htmlFor="question">Sua pergunta</label>
        <div className="composer-input">
          <input id="question" ref={input} required maxLength={500} value={question}
            disabled={action.busy} placeholder="Por onde começo?" onChange={event => setQuestion(event.target.value)} />
          <button disabled={action.busy || !question.trim()}>{action.problem ? 'Tentar novamente' : 'Enviar'}</button>
        </div>
      </form>
    </div>
  </>
}
