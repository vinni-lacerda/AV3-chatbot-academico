# Validação do MVP

A validação técnica usa três contas fictícias e atividades inventadas. A pessoa com perfil de novo integrante encontra orientações pela conversa, abre a referência e identifica quem procurar quando a base ainda tem uma lacuna. A demonstração pode ser repetida com o [roteiro local](demonstracao.md).

## Metas para o piloto

- Responder corretamente a pelo menos 4 de 5 perguntas cobertas, com fonte e data conferíveis em todas as respostas.
- Identificar as lacunas em 3 de 3 perguntas sem cobertura.
- Liberar zero registros pendentes, não autorizados, retirados ou substituídos em consultas novas.
- Permitir que um novo integrante descreva as etapas iniciais da atividade após consultar o chatbot. Anotar quais dúvidas ainda precisaram ser encaminhadas ao responsável.

## Perguntas e resultados com dados fictícios

| Pergunta ou cenário | Resultado observado |
|---|---|
| Como reenviar uma confirmação? | A orientação indica abrir a planilha, filtrar os cartões pendentes e usar o modelo de mensagem. Fonte **Guia de confirmação da feira**, manual fictício, 12/03/2025. |
| Quais são as etapas? Com a entrevista em revisão ou ajustes | O chatbot indica lacuna. O endpoint da fonte responde 404 ao novo integrante. |
| Quais são as etapas? Após aprovar a correção | O chatbot apresenta as etapas da versão 2, com autor e data de envio. |
| Quais são as etapas? Com a versão 3 pendente | A versão 2 aprovada ainda sustenta a resposta. |
| Quais são as etapas? Após aprovar a versão 3 | A resposta usa a orientação da versão 3. A fonte da versão 2 deixa de ficar disponível. |
| Qual é o orçamento das inscrições da feira? | O chatbot indica que a base é insuficiente e mostra **Beto Alves · Demo** como referência. O valor continua pendente de confirmação. |
| Quais são as etapas? Após retirar a versão aprovada | A nova consulta indica lacuna e a inspeção da fonte devolve 404. |
| Tentativa de aprovação com conta de integrante | A API responde 403. O estado pendente é preservado. |
| Retirada enquanto o seletor de IA aguarda | A API verifica novamente o estado da versão e exclui o trecho retirado do resultado. |

## Reproduzir

Com as dependências do README instaladas, rode no diretório `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

A suíte usa uma base em memória por padrão. Para exercitar o repositório em uma instância real do MongoDB, defina `$env:MVP_TEST_MONGO_URI = "mongodb://localhost:27017"` antes de executar o comando. A suíte usa um banco temporário com nome único para os testes.

Com a API rodando com dados fictícios e o frontend configurado em `frontend/.env`, rode no diretório `frontend`:

```powershell
npm.cmd exec -- playwright install chromium
npm.cmd run test:e2e
npm.cmd run build
```

Em Linux ou macOS, use `.venv/bin/python` e `npm`. Com Microsoft Edge disponível, defina `E2E_BROWSER_CHANNEL=msedge` para usar o navegador instalado.

Passaram 56 testes Python com MongoDB real e 3 testes de ponta a ponta no Edge. A instalação com `npm ci` e o build do frontend também passaram. As verificações de API exercitam permissões, transições, datas, retirada e correção de versões. Os testes de navegador cobrem o fluxo da entrevista, a retentativa após perda da resposta de rede, o cadastro e a aprovação de documentos e a consulta por teclado em uma tela de 390 px.

## Limitações da avaliação

A busca por palavras pode deixar de recuperar sinônimos, flexões e perguntas que exigem combinar trechos diferentes. A avaliação técnica usa dados fictícios. As metas de utilidade e a passagem de atividade com uma equipe universitária ainda precisam ser medidas no piloto. Os testes do Ollama usam respostas de provedor simuladas para verificar o contrato, a validação de índices e o tratamento de indisponibilidade.
