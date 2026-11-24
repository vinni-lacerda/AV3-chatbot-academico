# 🏗️ Backend — Passa o Bastão (Clean Architecture Agnóstica + SOLID + Flask + MongoDB)

Este diretório contém o backend em Python do projeto **Passa o Bastão**, projetado para ser **estritamente agnóstico a bibliotecas externas** em suas camadas de negócio (`domain` e `application` usam **100% Python padrão / stdlib**), enquanto toda entrega HTTP (incluindo os controllers agnósticos, documentação OpenAPI/Swagger e o adaptador do **Flask**), persistência (**MongoDB**), seleção opcional por IA local (**Ollama**) e criptografia ficam na camada `infrastructure/`.

---

## 🧭 Arquitetura em 3 Camadas (`domain`, `application`, `infrastructure`)

```mermaid
flowchart TD
    subgraph Infra["Infrastructure Layer (src/infrastructure/)"]
        FlaskApp["http/flask/ (Flask Blueprints & Route Adapter)"]
        HttpCore["http/ (Controllers agnósticos, AuthGuard, OpenAPI, HttpRequest/HttpResponse)"]
        MongoRepo["persistence/mongodb/ (MongoUserRepository & MongoKnowledgeRepository)"]
        OllamaAdapter["ai/ollama.py (OllamaSelector local via loopback)"]
        SecAdapters["security/ (BcryptPasswordHasher & JwtTokenProvider)"]
        CompRoot["container/ (DependencyContainer - Composition Root)"]
    end

    subgraph App["Application Layer (src/application/ - 100% Python Puro)"]
        UC["Use Cases (RegisterUser, AuthenticateUser, GetCurrentUser, ManageKnowledge, ConsultKnowledge) + DTOs"]
    end

    subgraph Dom["Domain Layer (src/domain/ - 100% Python Puro)"]
        Ent["Entities (User, UserRole, Status, QUESTIONS) + Exceptions"]
        Ports["Ports/Interfaces (IUserRepository, KnowledgeRepository, IPasswordHasher, ITokenProvider)"]
    end

    FlaskApp -->|"Adapta flask.request -> HttpRequest"| HttpCore
    HttpCore --> UC
    UC --> Ent
    UC --> Ports
    MongoRepo -.->|"Implementa"| Ports
    OllamaAdapter -.->|"Injeta seletor"| UC
    SecAdapters -.->|"Implementa"| Ports
```

---

## 📁 Estrutura de Diretórios

```text
backend/
├── Dockerfile                       # Imagem da API com execução automática do seed fictício (demo.py)
├── docker-compose.yml               # Orquestração MongoDB 7 + Backend Flask (base passa_o_bastao_demo)
├── Makefile                         # Automação (liberação de portas, docker, seed, testes)
├── start.sh                         # Script alternativo sem make para liberar portas e subir containers
├── openapi.json                     # Especificação OpenAPI 3.0.3 estática (Postman/Insomnia)
├── pyproject.toml                   # Metadados e configuração do Pytest
├── requirements.txt                 # Dependências externas (isoladas em infrastructure/)
├── .env.example                     # Exemplo de variáveis de ambiente
├── docker/
│   └── mongodb/
│       └── init-seed.js             # Inicialização de índices únicos da base no container MongoDB
├── src/
│   ├── main.py                      # Ponto de entrada que inicializa o Flask
│   ├── domain/                      # 100% Python puro (Entidades, Exceções e Contratos)
│   │   ├── knowledge.py             # Roteiro de entrevista, estados (Status) e exceções de conhecimento
│   │   ├── entities/
│   │   │   └── user.py              # Entidade User e Enum UserRole (RF01)
│   │   ├── exceptions/
│   │   │   └── domain_exceptions.py # Exceções de negócio
│   │   ├── repositories/
│   │   │   ├── knowledge_repository.py
│   │   │   └── user_repository.py   # Interface IUserRepository
│   │   └── services/
│   │       ├── password_hasher.py   # Interface IPasswordHasher
│   │       └── token_provider.py    # Interface ITokenProvider
│   ├── application/                 # 100% Python puro (Casos de Uso e DTOs)
│   │   ├── dtos/
│   │   │   └── auth_dtos.py
│   │   └── use_cases/
│   │       ├── register_user.py
│   │       ├── authenticate_user.py
│   │       ├── get_current_user.py
│   │       ├── manage_knowledge.py  # Ciclo de vida de atividades, relatos, documentos e revisões
│   │       └── consult_knowledge.py # Recuperação lexical com radicais/sinônimos e seleção opcional por IA
│   └── infrastructure/              # Camada externa (HTTP, Persistência, IA, Segurança, Config)
│       ├── ai/
│       │   └── ollama.py            # Adaptador do Ollama local com sanitização de prompt injection
│       ├── config/
│       │   └── settings.py          # Leitor de .env e variáveis de ambiente em Python puro
│       ├── container/
│       │   └── composition_root.py  # Injeção manual de dependências (Composition Root)
│       ├── http/                    # Entrega HTTP (Controllers agnósticos + OpenAPI + Adaptador Flask)
│       │   ├── contracts.py         # HttpRequest, HttpResponse e IController
│       │   ├── error_mapper.py      # Tradutor de DomainError para HttpResponse
│       │   ├── openapi_spec.py      # Especificação OpenAPI 3.0.3 em Python puro
│       │   ├── knowledge_openapi.py # Documentação OpenAPI das rotas de conhecimento
│       │   ├── middlewares/
│       │   │   └── auth_guard.py    # Validação de Bearer Token e RBAC (RF01)
│       │   ├── controllers/
│       │   │   ├── auth_controller.py
│       │   │   ├── docs_controller.py
│       │   │   ├── health_controller.py
│       │   │   └── knowledge_controller.py
│       │   └── flask/
│       │       ├── adapter.py       # Converte flask.request <-> HttpRequest / HttpResponse
│       │       └── app_factory.py   # Cria a aplicação Flask e registra os Blueprints
│       ├── persistence/
│       │   ├── demo.py              # Carga fictícia idempotente (usuários demo, atividade e documento aprovado)
│       │   ├── seed.py              # Seed idempotente das contas fictícias de demonstração
│       │   ├── mongodb/
│       │   │   ├── connection.py
│       │   │   ├── schema.py        # Validadores $jsonSchema e índices do MongoDB
│       │   │   └── repositories/
│       │   │       ├── mongo_knowledge_repository.py
│       │   │       └── mongo_user_repository.py
│       │   └── memory/
│       │       └── in_memory_user_repository.py
│       └── security/
│           ├── bcrypt_password_hasher.py
│           └── jwt_token_provider.py
└── tests/
    ├── unit/
    │   ├── test_domain_user.py
    │   ├── test_auth_use_cases.py
    │   ├── test_http_layer.py
    │   ├── test_ollama.py
    │   ├── test_security_and_repositories.py
    │   └── test_seed.py
    └── integration/
        ├── test_auth_controller.py
        └── test_knowledge_workflow.py
```

---

## 🚀 Como Executar com Docker

O [README principal](../README.md#instalação-e-execução) documenta o ambiente local da SPA e da API com dados fictícios na base `passa_o_bastao_demo`.

### Opção A: Usando `make`
Para liberar automaticamente as portas `27017` e `8000` (caso outro container esteja usando), construir a imagem, iniciar o MongoDB + Backend e popular o banco com os dados fictícios de demonstração:

```bash
cd backend
make up
```

Para parar os containers ou ver os logs:
```bash
make down
make logs
```

### Opção B: Sem `make` (Linux, macOS ou Git Bash no Windows)
O script `start.sh` executa exatamente os mesmos passos do `make up` (libera as portas `27017` e `8000` e sobe os containers com o seed fictício):

```bash
cd backend
bash start.sh
```

### Opção C: Sem `make` (Comandos diretos do Docker em qualquer sistema operacional)
Caso esteja no Windows (PowerShell / CMD) ou prefira rodar os comandos do Docker diretamente:

1. *(Opcional)* Se houver outro container usando a porta `27017` ou `8000`, pare-o antes:
   ```bash
   docker stop <nome_do_container>
   ```
2. Subir os containers e aplicar o seed fictício:
   ```bash
   cd backend
   docker compose up --build --force-recreate -d
   ```
3. Ver os logs em tempo real:
   ```bash
   docker compose logs -f
   ```
4. Parar os containers:
   ```bash
   docker compose down
   ```

---

## 🌱 Contas Fictícias de Demonstração (`demo.py`)

O Docker Compose configura a base `passa_o_bastao_demo` e carrega os dados fictícios. Para executar `python -m infrastructure.persistence.demo` ou `make seed` fora do Compose, defina `MONGODB_DB_NAME=passa_o_bastao_demo` no ambiente ou no `.env` do backend antes da carga. Consulte os passos de execução direta no [README principal](../README.md#instalação-e-execução).

A senha de demonstração para as três contas fictícias é **`Bastao-Demo-2026!`**.

| Nome | E-mail | Perfil (`RF01`) |
|---|---|---|
| Lia Monteiro · Demo | `lia@demo.example` | `integrante` (registra entrevistas e documentos) |
| Beto Alves · Demo | `beto@demo.example` | `responsavel` (cadastra atividades e revisa conteúdos) |
| Ada Wong - Demo | `ada@demo.example` | `novo_integrante` (consulta orientações aprovadas) |

### Conexão no DataGrip / MongoDB Compass
- **Host:** `localhost`
- **Port:** `27017`
- **Authentication:** `No auth`
- **Database:** `passa_o_bastao_demo`
- **URL:** `mongodb://localhost:27017/passa_o_bastao_demo`

---

## 📖 Documentação Swagger (OpenAPI 3.0.3) e Endpoints

Com o backend rodando em `http://localhost:8000`:
- **Swagger UI Interativo:** http://localhost:8000/docs
- **JSON OpenAPI 3.0.3:** http://localhost:8000/openapi.json
- **Arquivo estático para Postman/Insomnia:** `backend/openapi.json`

| Método | Rota | Autenticação | Descrição |
|---|---|---|---|
| `GET` | `/docs` | Pública | Interface interativa Swagger UI |
| `GET` | `/openapi.json` | Pública | Especificação OpenAPI 3.0.3 em JSON |
| `GET` | `/api/v1/health` | Pública | Healthcheck do serviço |
| `POST` | `/api/v1/auth/register` | Pública | Cadastra novo integrante com perfil `novo_integrante` (`RF01`) |
| `POST` | `/api/v1/auth/login` | Pública | Autentica integrante e retorna Bearer Token JWT (`RF01`) |
| `GET` | `/api/v1/auth/me` | Bearer JWT | Retorna dados e permissões calculadas do usuário autenticado |
| `GET` | `/api/v1/auth/permissions/review-check` | Bearer JWT (`responsavel`) | Valida permissão exclusiva de revisão (`403` para demais perfis) |

O [contrato das rotas de conhecimento](../docs/arquitetura.md#api) documenta atividades, entrevistas, revisão, fontes e chat.
O [esquema MongoDB](../docs/arquitetura.md#mongodb) descreve os validadores, os índices e como atualizar uma base do MVP.

---

## 🧪 Executar Testes Localmente

### Linux / macOS / Git Bash:
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
```
*(Ou `make test` se tiver o `make` instalado).*

### Windows (PowerShell / CMD):
```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pytest -v
```

Para testar os validadores com MongoDB 7, defina `MVP_TEST_MONGO_URI` com a URI do servidor de teste antes de executar o pytest. A suíte cria e remove bases temporárias próprias. Sem essa variável, o fluxo da API usa mongomock e o teste dos validadores é pulado.
