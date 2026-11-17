import { useEffect, useRef, useState } from 'react'
import { ActivitySelect, Alert, Badge, PageHeader, Resource, useAction, useResource } from '../ui'

const documentFields = [
  ['title', 'Título do documento', 160],
  ['origin', 'Origem ou referência', 350],
  ['date', 'Data do documento', 10],
  ['text', 'Conteúdo autorizado', 8000],
]

function ContributionForm({ record, questions, api, onClose }) {
  const [saved, setSaved] = useState(record)
  const initial = record.versions.at(-1)
  const [content, setContent] = useState(initial.content)
  const [authorized, setAuthorized] = useState(initial.authorized)
  const [step, setStep] = useState(() => {
    const unanswered = questions.findIndex(question => !initial.content[question.key])
    return unanswered === -1 ? questions.length : unanswered
  })
  const [preview, setPreview] = useState(record.kind === 'entrevista' && step === questions.length)
  const [editingFromPreview, setEditingFromPreview] = useState(false)
  const [submission, setSubmission] = useState(null)
  const heading = useRef(null)
  const action = useAction()
  const isInterview = record.kind === 'entrevista'
  const fields = isInterview ? questions.map(({ key, title }) => [key, title]) : documentFields

  function remember() {
    const draft = saved.versions.at(-1)
    return api(`/records/${record.id}/draft`, {
      method: 'PUT',
      body: { version: draft.number, revision: saved.revision, content, authorized },
    }).then(updated => {
      setSaved(updated)
      return { version: updated.versions.at(-1).number, revision: updated.revision }
    })
  }

  function move(next) {
    setStep(next)
    setPreview(next === questions.length)
    requestAnimationFrame(() => heading.current?.focus())
  }

  function submit() {
    action.run(async () => {
      const target = submission || await remember()
      setSubmission(target)
      await api(`/records/${record.id}/submit`, { method: 'POST', body: target })
      onClose('Relato enviado e aguardando revisão.')
    })
  }

  const question = questions[step]
  return <section className="card editor">
    <div className="card-heading">
      <div><Badge status="rascunho" /><h2>{isInterview ? 'Entrevista guiada' : 'Fonte documental'}</h2></div>
      <button type="button" className="secondary" disabled={action.busy} onClick={() => onClose('')}>Voltar aos rascunhos</button>
    </div>
    {isInterview && <div className="progress">
      <span>{preview ? 'Conferência final' : `Pergunta ${step + 1} de ${questions.length}`}</span>
      <progress aria-label="Progresso da entrevista" value={preview ? questions.length : step + 1} max={questions.length} />
    </div>}
    {preview ? <>
      <h3 tabIndex={-1} ref={heading}>Confira antes de enviar</h3>
      <dl className="summary-list">
        {fields.map(([key, title]) => <div key={key}>
          <dt>{title}</dt>
          <dd className="preserve">{content[key]?.trim() || 'Campo a preencher'}</dd>
          <button type="button" className="link" disabled={action.busy || Boolean(submission)} onClick={() => {
            if (isInterview) {
              setEditingFromPreview(true)
              move(questions.findIndex(item => item.key === key))
            } else setPreview(false)
          }} aria-label={`Editar ${title.toLowerCase()}`}>Editar</button>
        </div>)}
      </dl>
      <label className="checkbox">
        <input type="checkbox" checked={authorized} disabled={Boolean(submission) || action.busy} onChange={event => setAuthorized(event.target.checked)} />
        Confirmo que este conteúdo está autorizado para uso pelo projeto.
      </label>
      <Alert>{action.problem}</Alert>
      <div className="actions">
        <button type="button" disabled={action.busy || !authorized || fields.some(([key]) => !content[key]?.trim())}
          onClick={submit}>{submission && action.problem ? 'Tentar enviar novamente' : 'Enviar para revisão'}</button>
        <button type="button" className="secondary" disabled={action.busy || Boolean(submission)} onClick={() => action.run(async () => {
          await remember()
          onClose('Rascunho salvo.')
        })}>Salvar e sair</button>
      </div>
    </> : <form onSubmit={event => {
      event.preventDefault()
      action.run(async () => {
        await remember()
        if (isInterview) {
          move(editingFromPreview ? questions.length : step + 1)
          setEditingFromPreview(false)
        } else {
          setPreview(true)
          requestAnimationFrame(() => heading.current?.focus())
        }
      })
    }}>
      {isInterview ? <>
        <div className="prompt" tabIndex={-1} ref={heading} aria-label={question.prompt}>
          <span className="speaker">Passa o Bastão</span><p>{question.prompt}</p>
        </div>
        <label>Sua resposta
          <textarea required maxLength={1500} rows={5} value={content[question.key] || ''} disabled={action.busy}
            onChange={event => setContent({ ...content, [question.key]: event.target.value })} />
        </label>
      </> : documentFields.map(([key, title, length]) => {
        const props = {
          required: true, disabled: action.busy, value: content[key] || '',
          onChange: event => setContent({ ...content, [key]: event.target.value }),
        }
        return <label key={key}>{title}
          {key === 'text' ? <textarea {...props} maxLength={length} rows={6} />
            : <input {...props} type={key === 'date' ? 'date' : 'text'} maxLength={length} />}
        </label>
      })}
      <Alert>{action.problem}</Alert>
      <div className="actions">
        <button disabled={action.busy || (isInterview && !content[question.key]?.trim())}>
          {isInterview && step < questions.length - 1 && !editingFromPreview ? 'Salvar e avançar' : 'Conferir conteúdo'}
        </button>
        <button type="button" className="secondary" disabled={action.busy} onClick={() => action.run(async () => {
          await remember()
          onClose('Rascunho salvo.')
        })}>Salvar e sair</button>
        {isInterview && step > 0 && !editingFromPreview && <button type="button" className="link" disabled={action.busy} onClick={() => move(step - 1)}>Pergunta anterior</button>}
      </div>
    </form>}
  </section>
}

export function Interview({ api, activities, editorRequest }) {
  const [kind, setKind] = useState('entrevista')
  const [activity, setActivity] = useState('')
  const [current, setCurrent] = useState(null)
  const [notice, setNotice] = useState('')
  const requestId = useRef(null)
  const action = useAction()
  const questions = useResource(api, '/interview/questions')
  const drafts = useResource(api, '/records?view=mine&status=rascunho')

  useEffect(() => {
    if (editorRequest) {
      setCurrent(editorRequest.record)
      setNotice('')
    }
  }, [editorRequest])

  function close(message) {
    setCurrent(null)
    setNotice(message)
    drafts.reload()
  }

  return <>
    <PageHeader title="Registrar conhecimento">Compartilhe sua experiência ou cadastre um documento autorizado.</PageHeader>
    {current ? <Resource state={questions}>{({ items }) => <ContributionForm key={`${current.id}/${current.versions.at(-1).number}`}
      record={current} questions={items} api={api} onClose={close} />}</Resource> : <>
      {notice && <p className="notice" role="status">{notice}</p>}
      <form className="card editor" onSubmit={event => {
        event.preventDefault()
        action.run(async () => {
          requestId.current ??= crypto.randomUUID()
          const draft = await api('/records', {
            method: 'POST', body: { activity_id: activity, kind, id: requestId.current },
          })
          requestId.current = null
          setNotice('')
          if (draft.versions.at(-1).status === 'rascunho') setCurrent(draft)
          else close('Este registro já foi enviado. Consulte a situação em Registros.')
        })
      }}>
        <h2>Novo registro</h2>
        {activities.length === 0 && <p className="muted">Um responsável precisa cadastrar a primeira atividade.</p>}
        <ActivitySelect activities={activities} value={activity} onChange={value => {
          requestId.current = null
          setActivity(value)
        }} required empty="Selecione uma atividade" disabled={action.busy} />
        <label>Tipo de registro
          <select value={kind} disabled={action.busy} onChange={event => {
            requestId.current = null
            setKind(event.target.value)
          }}>
            <option value="entrevista">Entrevista guiada</option>
            <option value="documento">Fonte documental</option>
          </select>
        </label>
        <Alert>{action.problem}</Alert>
        <button disabled={action.busy || !activity}>Criar rascunho</button>
      </form>
      <div className="card draft-list">
        <div className="card-heading"><h2>Seus rascunhos</h2><button className="link" type="button" onClick={drafts.reload}>Atualizar</button></div>
        <Resource state={drafts}>{({ items }) => items.length ? items.map(record => <div className="draft-row" key={record.id}>
          <div><strong>{activities.find(item => item.id === record.activity_id)?.title}</strong>
            <small>{record.kind === 'entrevista' ? 'Entrevista' : 'Documento'} · versão {record.versions.at(-1).number}</small></div>
          <button className="secondary" type="button" onClick={() => {
            setCurrent(record)
            setNotice('')
          }}>Retomar rascunho</button>
        </div>) : <p className="muted">Nenhum rascunho salvo.</p>}</Resource>
      </div>
    </>}
  </>
}
