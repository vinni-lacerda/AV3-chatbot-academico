# Arquitetura e dados do MVP

A SPA React consome a API Flask em `/api/v1`. O container de dependências existente conecta os casos de uso aos repositórios PyMongo. O sistema atende um projeto universitário por instância.

## Permissões

| Operação | Novo integrante | Integrante | Responsável |
|---|---|---|---|
| Consultar a base, atividades e fontes aprovadas | Sim | Sim | Sim |
| Criar, salvar e enviar rascunhos próprios | — | Sim | Sim |
| Acompanhar decisões e criar novas versões de registros próprios | — | Sim | Sim |
| Cadastrar atividades | — | — | Sim |
| Ver conteúdo enviado para revisão e registrar decisões | — | — | Sim |

A API recebe `Authorization: Bearer <token>`, recarrega a conta ativa e aplica as permissões atuais. O cadastro público atribui apenas o perfil `novo_integrante`. A equipe atribui perfis adicionais na base conforme seu processo de provisionamento. A sessão é guardada na aba do navegador e o usuário pode encerrá-la com **Sair**. A biblioteca mostra histórico ao autor e versões enviadas ao responsável. Outros integrantes recebem somente conteúdo aprovado e autorizado, sem observações internas de revisão.

## MongoDB

| Coleção | Dados |
|---|---|
| `users` | ID de referência (`id`), nome, e-mail, hash de senha, papéis, situação da conta e datas BSON. O RA é opcional. `id` e `email` têm índices únicos. |
| `activities` | UUID em `_id`, título, descrição e responsável de referência (`responsible.id`, `responsible.name`). Para cadastrar uma atividade, o responsável deve ter uma conta ativa com o papel `responsavel`. |
| `knowledge_records` | UUID em `_id`, `activity_id`, tipo (`entrevista` ou `documento`), autor, datas em UTC e contador `revision` para controle de concorrência. As versões guardam o conteúdo, a autorização e as decisões. Os índices cobrem atividade, autor e estado das versões. |

Na primeira conexão, a API cria as coleções que faltam com validadores `$jsonSchema`, atualiza os validadores das que já existem via `collMod` e garante os índices. A carga de demonstração passa pela mesma inicialização. A credencial de inicialização precisa poder listar e criar coleções, alterar seus validadores e criar índices. A operação pode ser repetida e não reescreve os documentos.

Ao atualizar uma base do MVP, atividades já gravadas sem responsável continuam legíveis. Para corrigi-las, localize-as com `db.activities.find({ responsible: null })` e atribua a cada uma um responsável ativo de `users`, preenchendo `responsible` com o `id` e o `name` dessa conta. Novas inserções e atualizações precisam passar pelo validador. Em mudanças futuras, adapte o validador e planeje uma migração explícita para campos que precisem ser preenchidos ou convertidos nos documentos existentes.

Cada versão tem número, editor, datas, conteúdo, autorização e revisões. As fontes documentais ficam no conteúdo da versão, com título, origem, data de referência (AAAA-MM-DD) e texto. A fonte de uma entrevista são as seis respostas daquela versão. Cada revisão inclui revisor, decisão, data em UTC e observação. A API exige observação ao solicitar ajustes, valida as referências a atividades e versões e obtém autor e revisor da conta autenticada. O MongoDB valida a estrutura dos documentos sem consultar outras coleções.

Para carregar dados fictícios, siga o [roteiro de demonstração](demonstracao.md). A carga é optativa para desenvolvimento e teste e pode ser reaplicada sem recriar conteúdo aprovado ou retirar decisões.

O fluxo começa em **Rascunho** e passa a **Aguardando revisão** no envio. O responsável pode aprovar ou pedir ajustes. O autor pode abrir uma nova versão após aprovação, solicitação de ajustes ou retirada. O documento MongoDB é atualizado atomicamente com uma condição sobre a revisão anterior, o que impede uma decisão baseada em uma versão concorrente. A versão aprovada anterior continua ativa enquanto houver correções. Quando a substituta é aprovada, a anterior fica **Substituída** na mesma escrita. A retirada é imediata para novas consultas, inclusive para o endpoint da fonte. O histórico já carregado na aba pode conter uma resposta anterior. Retirar a versão atual preserva o histórico e encerra seu uso na base.

## Consulta

A busca considera apenas versões **Aprovadas** com autorização confirmada. Ela normaliza acentos, remove palavras frequentes, aplica redução morfológica de sufixos em português (plural, gênero e flexões verbais) e mapeia sinônimos recorrentes do domínio acadêmico. A atividade é identificada por seleção explícita, título citado na pergunta ou atividade inferida no turno anterior. As respostas da entrevista são trechos individuais. Os documentos usam parágrafos, com limite de tamanho por trecho.

Os radicais e termos canônicos da pergunta são comparados com o trecho e com o título do documento, tolerando variação lexical quando a pergunta combina múltiplos termos específicos. Perguntas sobre um tópico do roteiro também exigem evidência desse tópico. A busca ordena até seis trechos por correspondência textual e retorna até três com título, atividade, origem, autor, versão e data. Para entrevistas, a data é a do envio da versão citada. Para documentos, é a data declarada na fonte original. Quando a evidência é insuficiente, a API indica a lacuna e, quando disponível, o responsável ativo pela atividade.

Com o Ollama habilitado, o modelo recebe somente a pergunta e os trechos aprovados com seus títulos, via loopback (`127.0.0.1`), após sanitização contra instruções embutidas (*prompt injection*) e caracteres de controle. Modelos com sufixo `:cloud` ou `-cloud` são recusados na configuração. Ele devolve índices de um JSON estruturado. A API valida os índices e monta a resposta com o texto original aprovado. O modelo não recebe ferramentas, dados de login, observações de revisão ou documentos pendentes. Erros, timeouts e índices inválidos ativam a busca extrativa sem expor segredos. Antes de devolver cada trecho, a API verifica se a versão ainda está disponível. A consulta lê diretamente o MongoDB e não mantém índice de busca externo nem cache de conteúdo.

## API

| Método e rota sob `/api/v1` | Entrada e resultado |
|---|---|
| `GET /health` | Estado da API. Acesso público. |
| `POST /auth/login`, `GET /auth/me` | Login com `email` e `password`. Consulta de identidade e permissões. |
| `GET /activities` | Lista de atividades em `items`. |
| `GET /activities/{id}` | Dados de uma atividade, incluindo o responsável de referência. |
| `POST /activities` | `title`, `description` e `responsible_id` obrigatórios. |
| `GET /interview/questions` | Roteiro ordenado em `items`. |
| `GET /records` | `view=library\|mine\|review` e filtros opcionais `activity_id`, `status` e `since` (AAAA-MM-DD). Retorna registros e versões visíveis em `items`. |
| `POST /records` | `id` (UUID definido pelo cliente para retentativas), `activity_id` e `kind` (`entrevista` ou `documento`). |
| `PUT /records/{id}/draft` | `version`, `revision`, `content` e `authorized`. Salva as respostas ou os dados do documento no rascunho. |
| `POST /records/{id}/submit` | `version` e `revision`. Envia para revisão. |
| `POST /records/{id}/revise` | `version` e `revision`. Cria uma nova versão em rascunho. |
| `POST /records/{id}/review` | `version`, `revision`, `decision` (`aprovado`, `ajustes_solicitados` ou `retirado`) e `note`. |
| `POST /chat` | `question`, `activity_id` opcional e `context_activity_id` do turno anterior. Retorna `answer`, `gap`, `sources`, `activity_id`, `responsible` e `mode`. |
| `GET /sources/{id}/{version}` | Conteúdo da versão enquanto aprovada e autorizada. |

As operações de criação respondem com 201. As demais operações bem-sucedidas respondem com 200. O corpo de erro contém `detail` e `error_code`. Dados inválidos retornam 400, token ausente ou inválido retorna 401, falta de papel retorna 403, recurso indisponível retorna 404 e conflito de versão retorna 409.
