import { useState } from 'react'
import { ActivitySelect, Alert, Badge, dateLabel, PageHeader, Resource, statusNames, useAction, useResource } from '../ui'

const labels = {
  etapas: 'Etapas', recursos: 'Recursos', dificuldades: 'Dificuldades', solucoes: 'Soluções',
  decisoes: 'Decisões', recomendacoes: 'Recomendações', title: 'Título', origin: 'Origem',
  date: 'Data do documento', text: 'Conteúdo',
}

function VersionContent({ version }) {
  return <>
    <dl className="source-content">
      {Object.entries(version.content).map(([key, value]) => <div key={key}>
        <dt>{labels[key]}</dt><dd className="preserve">{value ? (key === 'date' ? dateLabel(value) : value) : '—'}</dd>
      </div>)}
    </dl>
    {version.submitted_at && <p className="muted">Enviada em {dateLabel(version.submitted_at)}</p>}
    {version.reviews?.length > 0 && <ul className="review-history">
      {version.reviews.map((review, index) => <li key={index}>
        <strong>{statusNames[review.decision]}</strong> por {review.reviewer.name} em {dateLabel(review.date)}
        {review.note && <p className="preserve">{review.note}</p>}
      </li>)}
    </ul>}
  </>
}

function ReviewForm({ busy, version, onReview }) {
  const [note, setNote] = useState('')
  return <form className="review-form" onSubmit={event => {
    event.preventDefault()
    onReview(event.nativeEvent.submitter.value, note)
  }}>
    <label>Observação da revisão
      <textarea rows={2} maxLength={1500} disabled={busy} value={note} onChange={event => setNote(event.target.value)} />
    </label>
    <div className="actions">
      {version.status === 'pendente' ? <>
        <button type="submit" value="aprovado" disabled={busy}>Aprovar</button>
        <button type="submit" className="secondary" value="ajustes_solicitados" disabled={busy || !note.trim()}>Solicitar ajustes</button>
      </> : <button type="submit" className="danger" value="retirado" disabled={busy}>Retirar da consulta</button>}
    </div>
  </form>
}

function RecordCard({ record, activity, api, mode, onEdit, reload, user, onNotice }) {
  const action = useAction()
  const versions = record.versions.toReversed()
  const latest = versions[0]
  const owner = record.author.id === user.id && user.permissions.can_record_knowledge
  const title = record.kind === 'documento'
    ? latest.content.title || 'Documento sem título'
    : `Entrevista · ${activity}`

  function update(version, endpoint, data) {
    action.run(async () => {
      const updated = await api(`/records/${record.id}/${endpoint}`, {
        method: 'POST', body: { version: version.number, revision: record.revision, ...data },
      })
      if (endpoint === 'revise') onEdit(updated)
      else {
        onNotice(`Decisão registrada. ${statusNames[data.decision]}.`)
        reload()
      }
    })
  }

  return <article className="card record">
    <div className="card-heading">
      <div><h2>{title}</h2><p className="muted">{activity} · {record.author.name} · {dateLabel(record.created_at)}</p></div>
      <Badge status={latest.status} />
    </div>
    {versions.map(version => <details className="version" key={version.number}>
      <summary>
        <strong>Versão {version.number}</strong>
        <span>{dateLabel(version.updated_at)} · {statusNames[version.status]}</span>
      </summary>
      <div className="version-body">
        <VersionContent version={version} />
        {mode === 'review' && ['pendente', 'aprovado'].includes(version.status) && <ReviewForm
          busy={action.busy} version={version} onReview={(decision, note) => update(version, 'review', { decision, note })} />}
      </div>
    </details>)}
    {mode === 'library' && owner && <div className="actions">
      {latest.status === 'rascunho' && <button className="secondary" type="button" onClick={() => onEdit(record)}>Retomar rascunho</button>}
      {['aprovado', 'ajustes_solicitados', 'retirado'].includes(latest.status) && <button className="secondary" type="button"
        disabled={action.busy} onClick={() => update(latest, 'revise', {})}>
        {latest.status === 'ajustes_solicitados' ? 'Corrigir e reenviar' : 'Criar nova versão'}
      </button>}
    </div>}
    <Alert>{action.problem}</Alert>
  </article>
}

function NewActivity({ api, user, onCreated }) {
  const action = useAction()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [open, setOpen] = useState(false)

  if (!open) return <button type="button" onClick={() => setOpen(true)}>Cadastrar atividade</button>

  return <form className="card editor" onSubmit={event => {
    event.preventDefault()
    action.run(async () => {
      await api('/activities', {
        method: 'POST', body: { title, description, responsible_id: user.id },
      })
      setTitle('')
      setDescription('')
      setOpen(false)
      onCreated()
    })
  }}>
    <h2>Nova atividade</h2>
    <label>Título da atividade<input required maxLength={120} value={title} onChange={event => setTitle(event.target.value)} /></label>
    <label>Descrição<textarea required maxLength={1000} rows={3} value={description} onChange={event => setDescription(event.target.value)} /></label>
    <p className="muted">Responsável de referência: {user.name}</p>
    <Alert>{action.problem}</Alert>
    <div className="actions">
      <button disabled={action.busy}>Salvar atividade</button>
      <button type="button" className="secondary" disabled={action.busy} onClick={() => {
        action.clear()
        setOpen(false)
      }}>Cancelar</button>
    </div>
  </form>
}

export function Records({ api, user, activities, reloadActivities, mode, onEdit }) {
  const reviewing = mode === 'review'
  const [activity, setActivity] = useState('')
  const [status, setStatus] = useState(reviewing ? 'pendente' : '')
  const [since, setSince] = useState('')
  const [notice, setNotice] = useState('')
  const [mine, setMine] = useState(false)
  const filters = new URLSearchParams({ view: reviewing ? 'review' : mine ? 'mine' : 'library' })
  if (activity) filters.set('activity_id', activity)
  if (status) filters.set('status', status)
  if (since) filters.set('since', since)
  const records = useResource(api, `/records?${filters}`)

  return <>
    <PageHeader title={reviewing ? 'Revisão de conteúdo' : 'Registros por atividade'}>
      {reviewing ? 'Confira o material antes de liberar seu uso nas consultas.' : 'Explore os registros e acompanhe o histórico de versões a que você tem acesso.'}
    </PageHeader>
    {!reviewing && user.permissions.can_review_knowledge && <div className="toolbar">
      <NewActivity api={api} user={user} onCreated={() => {
        reloadActivities()
        setNotice('Atividade cadastrada.')
      }} />
    </div>}
    <div className="card filters">
      <ActivitySelect activities={activities} value={activity} onChange={setActivity} />
      <label>Situação
        <select value={status} onChange={event => setStatus(event.target.value)}>
          <option value="">Todas as situações</option>
          {Object.entries(statusNames).map(([key, text]) => <option key={key} value={key}>{text}</option>)}
        </select>
      </label>
      <label>Atualizado a partir de<input type="date" value={since} onChange={event => setSince(event.target.value)} /></label>
      {!reviewing && user.permissions.can_record_knowledge && <label className="checkbox">
        <input type="checkbox" checked={mine} onChange={event => setMine(event.target.checked)} /> Meus registros
      </label>}
      <button type="button" className="secondary" onClick={records.reload}>Atualizar</button>
    </div>
    {notice && <p className="notice" role="status">{notice}</p>}
    <Resource state={records}>{({ items }) => items.length
      ? <div className="records">{items.map(record => <RecordCard key={record.id} record={record}
        activity={activities.find(item => item.id === record.activity_id)?.title} api={api}
        mode={mode} user={user} onEdit={onEdit} reload={records.reload} onNotice={setNotice} />)}</div>
      : <p className="empty">Nenhum registro encontrado com esses filtros.</p>
    }</Resource>
  </>
}
