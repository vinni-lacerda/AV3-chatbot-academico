import { expect, test } from '@playwright/test'
import { randomUUID } from 'node:crypto'

const password = 'Bastao-Demo-2026!'

async function login(page, email) {
  await page.goto('/')
  await page.getByLabel('E-mail').fill(email)
  await page.getByLabel('Senha').fill(password)
  await page.getByRole('button', { name: 'Entrar' }).click()
  await expect(page.getByRole('heading', { name: 'Consultar conhecimento' })).toBeVisible()
}

async function ask(page, question) {
  await page.getByLabel('Sua pergunta').fill(question)
  await page.getByLabel('Sua pergunta').press('Enter')
}

test('encontra a orientação de ambiente após consultar outra atividade', async ({ page }) => {
  await login(page, 'ada@demo.example')
  const activity = page.getByRole('combobox', { name: 'Atividade', exact: true })
  const setupQuestion = 'Como iniciar a API localmente?'

  await ask(page, 'Como solicitar uma sala?')
  await expect(page.getByText(/confira o calendário de espaços/)).toBeVisible()
  await ask(page, setupQuestion)
  await expect(page.getByText(/execute as migrações/)).toBeVisible()

  await activity.selectOption({ label: 'Reserva de salas' })
  await ask(page, setupQuestion)
  const retry = page.getByRole('button', { name: 'Buscar em todas as atividades' })
  await expect(retry).toBeVisible()
  await retry.click()
  await expect(page.getByText(/execute as migrações/)).toHaveCount(2)
  await expect(activity).toHaveValue('')
})

test('registra, corrige, aprova, consulta e retira uma entrevista', async ({ browser, page }) => {
  const reviewer = await browser.newPage()
  const reader = await browser.newPage()
  const activity = `Oficina ${randomUUID().slice(0, 8)}`
  const excerpt = 'Abra a ficha da oficina e confira a lista de presença.'
  const revisedExcerpt = 'Separe a ficha de presença antes de abrir a oficina.'

  await login(reviewer, 'beto@demo.example')
  await reviewer.getByRole('button', { name: 'Registros', exact: true }).click()
  await reviewer.getByRole('button', { name: 'Cadastrar atividade' }).click()
  await reviewer.getByLabel('Título da atividade').fill(activity)
  await reviewer.getByLabel('Descrição').fill('Atividade fictícia criada para o teste de navegador.')
  await reviewer.getByRole('button', { name: 'Salvar atividade' }).click()
  await expect(reviewer.getByText('Atividade cadastrada.')).toBeVisible()

  await login(page, 'lia@demo.example')
  await page.getByRole('button', { name: 'Registrar', exact: true }).click()
  await page.getByRole('combobox', { name: 'Atividade', exact: true }).selectOption({ label: activity })
  await page.getByRole('button', { name: 'Criar rascunho' }).click()
  await page.getByLabel('Sua resposta').fill(excerpt)
  await page.getByRole('button', { name: 'Salvar e avançar' }).click()
  await expect(page.getByText('Pergunta 2 de 6')).toBeVisible()
  await page.getByRole('button', { name: 'Voltar aos rascunhos' }).click()
  await page.getByRole('button', { name: 'Retomar rascunho' }).first().click()
  await expect(page.getByText('Pergunta 2 de 6')).toBeVisible()

  const answers = [
    'Use a lista impressa e o material da oficina.',
    'Algumas pessoas chegam depois do horário.',
    'Separe os materiais antes de abrir a sala.',
    'O grupo decidiu fazer a conferência presencial.',
    'Confirme a reserva da sala no dia anterior.',
  ]
  for (const [index, answer] of answers.entries()) {
    await page.getByLabel('Sua resposta').fill(answer)
    await page.getByRole('button', { name: index === 4 ? 'Conferir conteúdo' : 'Salvar e avançar' }).click()
  }
  await page.getByRole('checkbox', { name: /confirmo que este conteúdo/i }).check()
  await page.route('**/records/*/submit', async route => {
    await route.fetch()
    await route.abort()
  }, { times: 1 })
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByRole('alert')).toContainText('Não foi possível conectar')
  await page.getByRole('button', { name: 'Tentar enviar novamente' }).click()
  await expect(page.getByText('Relato enviado e aguardando revisão.')).toBeVisible()

  await login(reader, 'ada@demo.example')
  await expect(reader.getByRole('button', { name: 'Revisão', exact: true })).toHaveCount(0)
  await reader.getByRole('combobox', { name: 'Atividade', exact: true }).selectOption({ label: activity })
  await ask(reader, 'Quais são as etapas?')
  await expect(reader.getByText(/não há informação aprovada suficiente/i)).toBeVisible()

  await reviewer.getByRole('button', { name: 'Revisão', exact: true }).click()
  await reviewer.getByRole('combobox', { name: 'Atividade', exact: true }).selectOption({ label: activity })
  await reviewer.getByText('Versão 1', { exact: true }).click()
  await reviewer.getByLabel('Observação da revisão').fill('Detalhe a preparação da ficha.')
  await reviewer.getByRole('button', { name: 'Solicitar ajustes' }).click()
  await expect(reviewer.getByText(/Decisão registrada/)).toBeVisible()

  await page.getByRole('button', { name: 'Registros', exact: true }).click()
  await page.getByRole('combobox', { name: 'Atividade', exact: true }).selectOption({ label: activity })
  await page.getByRole('button', { name: 'Corrigir e reenviar' }).click()
  await page.getByRole('button', { name: 'Editar etapas' }).click()
  await page.getByLabel('Sua resposta').fill(revisedExcerpt)
  await page.getByRole('button', { name: 'Conferir conteúdo' }).click()
  await page.getByRole('checkbox', { name: /confirmo que este conteúdo/i }).check()
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByText('Relato enviado e aguardando revisão.')).toBeVisible()

  await reviewer.getByRole('button', { name: 'Atualizar' }).click()
  await reviewer.getByText('Versão 2', { exact: true }).click()
  await reviewer.getByRole('button', { name: 'Aprovar', exact: true }).click()
  await expect(reviewer.getByText('Decisão registrada. Aprovado.')).toBeVisible()

  await ask(reader, 'Quais são as etapas?')
  await expect(reader.getByText(revisedExcerpt, { exact: true })).toBeVisible()
  await reader.locator('.source summary').click()
  await expect(reader.getByText(/Entrevista · \d{2}\/\d{2}\/\d{4} · v2/)).toBeVisible()
  await expect(reader.locator('.source-body')).toContainText(revisedExcerpt)
  await reader.getByRole('button', { name: 'Registros', exact: true }).click()
  await reader.getByRole('button', { name: 'Consulta', exact: true }).click()
  await expect(reader.getByText('Fontes consultadas')).toBeVisible()

  await reviewer.getByRole('combobox', { name: 'Situação' }).selectOption('aprovado')
  await reviewer.getByText('Versão 2', { exact: true }).click()
  await reviewer.getByRole('button', { name: 'Retirar da consulta' }).click()
  await expect(reviewer.getByText('Decisão registrada. Retirado.')).toBeVisible()
  await reader.getByRole('button', { name: 'Nova conversa' }).click()
  await ask(reader, 'Quais são as etapas?')
  await expect(reader.getByText(/não há informação aprovada suficiente/i)).toBeVisible()
  await expect(reader.locator('.chat-reply')).toContainText('Beto Alves · Demo')
  await reviewer.close()
  await reader.close()
})

test('consulta fonte documental por teclado em uma tela estreita', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await login(page, 'ada@demo.example')
  await expect(page.getByText('Ada Wong - Demo', { exact: true })).toBeVisible()
  await ask(page, 'Como reenviar uma confirmação?')
  await expect(page.getByText(/filtre os cartões pendentes/)).toBeVisible()
  await expect(page.getByText(/12\/03\/2025/)).toBeVisible()
  await page.locator('.source summary').focus()
  await page.keyboard.press('Enter')
  await expect(page.locator('.source-body')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390)
})

test('cadastra e aprova uma fonte documental autorizada', async ({ browser, page }) => {
  const reviewer = await browser.newPage()
  const reader = await browser.newPage()
  const term = `protocolo${randomUUID().replaceAll('-', '').slice(0, 10)}`
  const title = `Guia de ${term}`
  const excerpt = `O ${term} indica como conferir o credenciamento no balcão da feira.`

  await login(page, 'lia@demo.example')
  await page.getByRole('button', { name: 'Registrar', exact: true }).click()
  await page.getByRole('combobox', { name: 'Atividade', exact: true }).selectOption({ label: 'Inscrições da feira' })
  await page.getByRole('combobox', { name: 'Tipo de registro' }).selectOption('documento')
  await page.getByRole('button', { name: 'Criar rascunho' }).click()
  await page.getByLabel('Título do documento').fill(title)
  await page.getByLabel('Origem ou referência').fill('Manual fictício de credenciamento')
  await page.getByLabel('Data do documento').fill('2025-04-08')
  await page.getByLabel('Conteúdo autorizado').fill(excerpt)
  await page.getByRole('button', { name: 'Conferir conteúdo' }).click()
  await expect(page.getByText(excerpt)).toBeVisible()
  await expect(page.getByRole('button', { name: 'Enviar para revisão' })).toBeDisabled()
  await page.getByRole('checkbox', { name: /confirmo que este conteúdo/i }).check()
  await page.getByRole('button', { name: 'Enviar para revisão' }).click()
  await expect(page.getByText('Relato enviado e aguardando revisão.')).toBeVisible()

  await login(reader, 'ada@demo.example')
  await ask(reader, `Como funciona o ${term}?`)
  await expect(reader.getByText(/não há informação aprovada suficiente/i)).toBeVisible()

  await login(reviewer, 'beto@demo.example')
  await reviewer.getByRole('button', { name: 'Revisão', exact: true }).click()
  const record = reviewer.getByRole('article').filter({ has: reviewer.getByRole('heading', { name: title }) })
  await record.getByText('Versão 1', { exact: true }).click()
  await record.getByRole('button', { name: 'Aprovar', exact: true }).click()
  await expect(reviewer.getByText('Decisão registrada. Aprovado.')).toBeVisible()

  await ask(reader, `Como funciona o ${term}?`)
  await expect(reader.getByText(excerpt, { exact: true })).toBeVisible()
  await expect(reader.getByText('Manual fictício de credenciamento · 08/04/2025 · v1')).toBeVisible()
  await reviewer.close()
  await reader.close()
})
