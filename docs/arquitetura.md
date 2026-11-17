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
| `users` | Identidade, perfis, hash de senha e situação da conta. Usa o esquema e os índices de autenticação já existentes. |
| `activities` | UUID, título, descrição e responsável de referência opcional. A API valida o responsável cadastrado contra `users`. |
| `knowledge_records` | UUID, atividade, tipo, autor, datas e revisão otimista. Contém as versões de conteúdo, autorização e decisões. |

O MongoDB cria as coleções por demanda. A API inicializa os índices de atividade, autor e estado das versões ao subir. Uma base que já contém usuários continua disponível, com as novas coleções criadas sem alteração nos documentos de `users`. A carga fictícia é optativa e pode ser reaplicada sem recriar conteúdo aprovado ou retirar decisões.

Cada versão tem um número, editor, datas, conteúdo, confirmação de autorização e decisões de revisão. Uma entrevista guarda seis respostas. Um documento guarda título, referência de origem, data e texto. Cada revisão guarda responsável, decisão, data e observação. Solicitar ajustes exige uma observação.

O fluxo começa em **Rascunho** e passa a **Aguardando revisão** no envio. O responsável pode aprovar ou pedir ajustes. O autor pode abrir uma nova versão após aprovação, solicitação de ajustes ou retirada. O documento MongoDB é atualizado atomicamente com uma condição sobre a revisão anterior, o que impede uma decisão baseada em uma versão concorrente. A versão aprovada anterior continua ativa enquanto houver correções. Quando a substituta é aprovada, a anterior fica **Substituída** na mesma escrita. A retirada é imediata para novas consultas, inclusive para o endpoint da fonte. O histórico já carregado na aba pode conter uma resposta anterior. Retirar a versão atual preserva o histórico e encerra seu uso na base.

## Consulta

A busca considera apenas versões **Aprovadas** com autorização confirmada. Ela normaliza acentos, remove palavras frequentes e identifica a atividade por seleção explícita, título citado na pergunta ou atividade inferida no turno anterior. As respostas da entrevista são trechos individuais. Os documentos usam parágrafos, com limite de tamanho por trecho.

Os termos específicos da pergunta precisam ocorrer no trecho ou no título do documento. Perguntas sobre um tópico do roteiro também exigem evidência desse tópico. A busca ordena até seis trechos por correspondência textual e retorna até três com título, atividade, origem, autor, versão e data. Para entrevistas, a data é a do envio da versão citada. Para documentos, é a data declarada na fonte original. Quando a evidência é insuficiente, a API indica a lacuna e, quando disponível, o responsável ativo pela atividade.

Com o Ollama habilitado, o modelo recebe somente a pergunta e os trechos aprovados com seus títulos, via loopback. Ele devolve índices de um JSON estruturado. A API valida os índices e monta a resposta com o texto original aprovado. O modelo não recebe ferramentas, dados de login, observações de revisão ou documentos pendentes. Erros, timeouts e índices inválidos ativam a busca extrativa. Antes de devolver cada trecho, a API verifica se a versão ainda está disponível. A consulta lê diretamente o MongoDB e não mantém índice de busca externo nem cache de conteúdo.

## API

| Método e rota sob `/api/v1` | Entrada e resultado |
|---|---|
| `GET /health` | Estado da API. Acesso público. |
| `POST /auth/login`, `GET /auth/me` | Login com `email` e `password`. Consulta de identidade e permissões. |
| `GET /activities` | Lista de atividades em `items`. |
| `POST /activities` | `title`, `description` e `responsible_id` opcional. |
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
