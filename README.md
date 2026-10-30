<div align="center">

# 🤝 Passa o Bastão

### Chatbot para transferência de conhecimento em projetos universitários

**Inteligência artificial · Memória organizacional · Conversação · Revisão humana**

![Status](https://img.shields.io/badge/status-em%20planejamento-blue)
![Foco](https://img.shields.io/badge/foco-gest%C3%A3o%20do%20conhecimento-0f766e)
![Projeto](https://img.shields.io/badge/projeto-acad%C3%AAmico-334155)

</div>

## 📌 Visão geral

O **Passa o Bastão** é uma proposta de chatbot que preserva experiências de integrantes de projetos universitários e ajuda novos membros a assumir atividades. A solução combina uma entrevista guiada para registrar conhecimento, revisão por um responsável e consulta por perguntas em linguagem natural.

Em empresas juniores, atléticas, centros acadêmicos e projetos de extensão, a saída de integrantes pode deixar lacunas sobre processos, decisões e dificuldades já resolvidas. A proposta é transformar parte desse conhecimento em orientações consultáveis, com autoria e data identificáveis.

**Estágio atual:** definição da proposta e do escopo. O repositório contém a documentação inicial; a aplicação ainda não foi implementada. As funcionalidades e a arquitetura abaixo representam o planejamento.

## 🧭 Sumário

- [Problema e objetivos](#problema-e-objetivos)
- [Recorte e público-alvo](#recorte-e-publico-alvo)
- [Funcionamento e diferencial](#funcionamento-e-diferencial)
- [Escopo e requisitos](#escopo-e-requisitos)
- [Arquitetura e tecnologias](#arquitetura-e-tecnologias)
- [Interfaces e dados](#interfaces-e-dados)
- [Validação e critérios de aceite](#validacao-e-criterios-de-aceite)
- [Planejamento e entregáveis](#planejamento-e-entregaveis)
- [Organização e uso do repositório](#organizacao-e-uso-do-repositorio)
- [Equipe e contexto acadêmico](#equipe-e-contexto-academico)
- [Referências](#referencias)

<a id="problema-e-objetivos"></a>
## 🎯 Problema e objetivos

**Problema central:** como registrar o conhecimento de quem deixa uma equipe e permitir que novos integrantes encontrem orientações confiáveis para assumir suas responsabilidades?

A hipótese é que uma entrevista guiada facilita o registro de etapas, exceções e aprendizados que poderiam não aparecer em uma documentação espontânea. Essa hipótese será avaliada no piloto.

**Objetivo geral:** desenvolver um protótipo de chatbot para registrar, organizar e disponibilizar conhecimento sobre atividades de um projeto universitário.

**Objetivos específicos:**

- Coletar relatos sobre atividades, dificuldades, decisões e recomendações.
- Organizar os registros por atividade, autor e data.
- Permitir revisão humana antes de liberar conteúdos para consulta.
- Responder perguntas usando informações aprovadas e indicando suas fontes.
- Reconhecer dúvidas que a base ainda não consegue responder.
- Avaliar a utilidade das orientações para um novo integrante.

<a id="recorte-e-publico-alvo"></a>
## 👤 Recorte e público-alvo

| Definição | Planejamento inicial |
|---|---|
| Unidade do piloto | Um único projeto universitário, a selecionar |
| Atividades cobertas | Conjunto pequeno de atividades, definido com a equipe participante |
| Fontes iniciais | Entrevistas e documentos autorizados do projeto |
| Resultado esperado | Protótipo que demonstre registro, revisão e consulta de conhecimento |
| Parceria | Nenhuma parceria confirmada até o momento |

| Perfil | Responsabilidade prevista |
|---|---|
| Integrante que registra conhecimento | Responder à entrevista e conferir o próprio relato |
| Novo integrante | Consultar orientações e apontar dúvidas ou informações incompletas |
| Responsável pelo projeto | Revisar conteúdos e manter os registros atualizados |

Os papéis poderão ser acumulados por uma mesma pessoa no piloto. As permissões deverão ser detalhadas antes da implementação.

<a id="funcionamento-e-diferencial"></a>
## 💬 Funcionamento e diferencial

O chatbot atuará em dois momentos: na coleta do conhecimento e na consulta por quem precisa executar uma atividade.

### Exemplo de entrevista

> **Bot:** Qual atividade você executava e que outra pessoa precisará assumir?
>
> **Integrante:** Eu organizava as inscrições da feira.
>
> **Bot:** Quais eram as etapas? Qual delas costumava causar problemas?
>
> **Integrante:** Algumas pessoas não recebiam a confirmação.
>
> **Bot:** Como vocês identificavam e resolviam isso?

Depois, um novo integrante poderá perguntar: **“Vou organizar as inscrições da próxima feira. Por onde começo e o que preciso conferir?”**

A resposta deverá reunir as orientações aprovadas e identificar sua origem e data. Quando faltar informação, o bot deverá explicitar a lacuna e indicar o responsável cadastrado pelo assunto, quando disponível.

### Fluxo proposto

```mermaid
flowchart TD
    A[Integrante inicia entrevista] --> B[Registra etapas e aprendizados]
    B --> C[Conteúdo organizado por atividade]
    C --> D{Responsável aprova?}
    D -->|Solicita ajustes| B
    D -->|Sim| E[Base de conhecimento aprovada]
    F[Novo integrante faz uma pergunta] --> G[Consulta à base aprovada]
    E --> G
    G --> H{Há informação suficiente?}
    H -->|Sim| I[Resposta com fonte e data]
    H -->|Não| J[Informa a lacuna e indica responsável]
```

O diferencial proposto é que o chatbot também ajuda a construir sua base de conhecimento. A entrevista busca registrar como o trabalho acontece, incluindo dificuldades e decisões que precisam ser contextualizadas.

<a id="escopo-e-requisitos"></a>
## 📋 Escopo e requisitos

### Requisitos funcionais da primeira versão

| ID | Funcionalidade prevista | Comportamento esperado |
|---|---|---|
| RF01 | Identificação e perfis | Distinguir quem registra, consulta e revisa conteúdos |
| RF02 | Entrevista guiada | Conduzir perguntas sobre etapas, dificuldades e recomendações |
| RF03 | Organização dos relatos | Relacionar registros a atividades, autores e datas |
| RF04 | Revisão humana | Aprovar, solicitar ajustes ou retirar conteúdo de consulta |
| RF05 | Consulta conversacional | Responder perguntas com base em registros aprovados |
| RF06 | Indicação de fontes | Exibir a origem e a data das informações utilizadas |
| RF07 | Tratamento de lacunas | Informar quando a base não oferece uma resposta suficiente |
| RF08 | Atualização de conhecimento | Permitir revisar registros que ficaram desatualizados |

### Requisitos de qualidade

- Interface compreensível para usuários sem conhecimento técnico.
- Preservação de autoria, data e situação de revisão dos registros.
- Aplicação das permissões no acesso aos dados e nas consultas do chatbot.
- Respostas vinculadas às informações disponíveis, com indicação de lacunas.
- Configurações e credenciais separadas dos arquivos versionados.

### Fora do escopo inicial

- Integração automática com WhatsApp, e-mail ou sistemas institucionais.
- Execução de tarefas em nome dos integrantes.
- Atendimento simultâneo a várias organizações.
- Treinamento de um modelo de linguagem próprio.

<a id="arquitetura-e-tecnologias"></a>
## 🏗️ Arquitetura e tecnologias

A arquitetura conceitual separa a entrevista, a aprovação dos registros e a elaboração de respostas. Sua implementação será definida após o levantamento dos requisitos do piloto.

```mermaid
flowchart LR
    U[Usuário] --> UI[Interface web]
    UI --> API[Aplicação e controle de acesso]
    API --> ENT[Entrevista e revisão]
    ENT --> DB[(Registros e metadados)]
    API --> BUS[Busca em conteúdos aprovados]
    DB --> BUS
    BUS --> IA[Elaboração da resposta com IA]
    IA --> API
```

A consulta poderá usar recuperação de informações para fornecer ao modelo os trechos aprovados relevantes à pergunta. O mecanismo de busca será escolhido conforme o volume de conteúdo e os resultados da avaliação. Conteúdos pendentes ou não autorizados não deverão compor as respostas.

| Camada | Decisão pendente |
|---|---|
| Interface | Tecnologia para as telas de conversa e revisão |
| Aplicação | Linguagem, framework e mecanismo de autenticação |
| Armazenamento | Banco para relatos, atividades e metadados |
| Busca | Estratégia de recuperação dos conteúdos aprovados |
| Inteligência artificial | Modelo, provedor e forma de integração |
| Hospedagem | Ambiente para demonstração do protótipo |

A seleção considerará familiaridade da equipe, custo, facilidade de demonstração e tratamento dos dados. Nenhuma dessas tecnologias está definida ou instalada neste repositório.

<a id="interfaces-e-dados"></a>
## 🖥️ Interfaces e dados

### Telas previstas

1. Identificação do usuário e de sua função.
2. Conversa para entrevista de passagem.
3. Revisão dos relatos e acompanhamento de aprovação.
4. Conversa para consulta, com fontes e datas.
5. Consulta e atualização dos registros por atividade.

### Informações previstas

| Registro | Campos iniciais |
|---|---|
| Integrante | Identificador, nome e função |
| Atividade | Título, descrição e responsável de referência |
| Relato | Conteúdo, atividade, autor, data e situação de revisão |
| Fonte documental | Título, origem, data e atividade relacionada |
| Revisão | Responsável, decisão, observação e data |

O roteiro deverá perguntar sobre sequência de execução, recursos utilizados, dificuldades, soluções e recomendações. O modelo de dados detalhado será produzido durante a implementação.

### Cuidados com as informações

O piloto deverá usar relatos e documentos autorizados, coletando apenas os dados necessários. Informações de terceiros sem autorização, senhas e credenciais não devem ser incluídas na base. Antes de usar serviços externos de IA, a equipe deverá definir quais dados poderão ser enviados, quem poderá consultá-los e como solicitar correção ou remoção.

Dados fictícios poderão ser utilizados nas primeiras demonstrações, identificados como exemplos.

<a id="validacao-e-criterios-de-aceite"></a>
## ✅ Validação e critérios de aceite

A validação proposta consiste em registrar uma atividade com alguém que a conhece e pedir a um novo integrante que busque orientações pelo chatbot. A equipe deverá preparar perguntas de referência, inclusive perguntas cujas respostas não estejam na base.

| Cenário de avaliação | Critério de aceite previsto |
|---|---|
| Conteúdo aguardando revisão | Não aparece nas respostas de consulta |
| Pergunta coberta pela base | Resposta compatível com o conteúdo aprovado, com fonte e data |
| Pergunta sem informação suficiente | Bot informa a lacuna sem inventar uma orientação |
| Conteúdo retirado de consulta | Deixa de ser utilizado nas respostas seguintes |
| Usuário sem permissão de revisão | Não consegue aprovar conteúdos |
| Novo integrante consulta uma atividade | Consegue localizar as etapas registradas e identificar dúvidas restantes |

Os resultados poderão registrar respostas corretas, fontes identificáveis e dúvidas que exigiram ajuda do antigo responsável. Metas quantitativas serão definidas antes do piloto; ainda não há resultados medidos.

<a id="planejamento-e-entregaveis"></a>
## 🗺️ Planejamento e entregáveis

- [x] Definir a ideia e o recorte inicial.
- [x] Documentar a proposta no README.
- [ ] Selecionar o projeto participante e validar o problema com seus integrantes.
- [ ] Levantar soluções similares e comparar pelo menos três alternativas.
- [ ] Definir o roteiro da entrevista e os requisitos detalhados.
- [ ] Prototipar as interfaces e o modelo de dados.
- [ ] Definir tecnologias, permissões e tratamento das informações.
- [ ] Implementar entrevista, revisão e consulta.
- [ ] Executar os cenários de validação e registrar os resultados.
- [ ] Preparar a demonstração e a documentação final.

| Entregável previsto | Conteúdo |
|---|---|
| Pré-projeto | Problema, objetivos, público e escopo |
| Levantamento de similares | Comparação de funcionalidades, limites e contribuição proposta |
| Documentação da solução | Requisitos, fluxos, arquitetura e modelo de dados |
| Protótipo das interfaces | Telas de entrevista, revisão e consulta |
| Aplicação demonstrável | Fluxo de passagem de uma atividade entre integrantes |
| Registro de avaliação | Cenários executados, resultados e limitações |
| Apresentação | Contexto, demonstração e aprendizados do projeto |

<a id="organizacao-e-uso-do-repositorio"></a>
## 📁 Organização e uso do repositório

Estrutura **sugerida**, a criar conforme as decisões técnicas. Atualmente, o projeto está documentado no `README.md`.

```text
.
├── README.md
├── docs/             # Requisitos, pesquisa, arquitetura e avaliação
├── prototypes/       # Protótipos e referências das interfaces
├── src/              # Implementação da aplicação
├── tests/            # Verificações dos comportamentos principais
└── presentation/     # Material da demonstração e apresentação
```

### Clonar o projeto

```bash
git clone https://github.com/vinni-lacerda/AV3-chatbot-academico.git
cd AV3-chatbot-academico
```

Para usar uma pasta local com outro nome:

```bash
git clone https://github.com/vinni-lacerda/AV3-chatbot-academico.git "chatbot IA"
cd "chatbot IA"
```

### Instalação e execução

Ainda não há uma aplicação executável. Os pré-requisitos, comandos de instalação, configuração das variáveis de ambiente e execução serão documentados quando a estrutura técnica estiver definida.

### Organização das contribuições

Como convenção inicial, cada tarefa deverá ter objetivo, responsável e critério de conclusão. Sugere-se trabalhar em branches por atividade, descrever as alterações em pull requests e manter a documentação alinhada ao que foi implementado. Credenciais e relatos privados não devem ser enviados ao repositório.

<a id="equipe-e-contexto-academico"></a>
## 👥 Equipe e contexto acadêmico

### Integrantes

Preencher os demais membros da equipe e ajustar a quantidade de linhas conforme o grupo. As responsabilidades de desenvolvimento serão combinadas após a definição das atividades.

| Integrante | Nome completo | RA | Responsabilidade |
|:--:|---|---|---|
| 1 | Vinicius Lacerda Santos | 12725210686 | A definir |
| 2 | Pedro Murilo Pereira | 122519964 | A definir |
| 3 | [Nome completo] | [RA] | A definir |
| 4 | [Nome completo] | [RA] | A definir |
| 5 | [Nome completo] | [RA] | A definir |

<a id="referencias"></a>
## 📚 Referências

- **Pré-Projeto UC HUB:** modelo fornecido para organizar integrantes, similares, usuários, processos e interfaces da proposta.
- **Batista et al. (2020).** [Mobile Applications and Discrete Event Systems: Low Cost Technology to Assist Stock Management in an Orthopaedic Clinic](https://www.dpublication.com/wp-content/uploads/2020/02/2-13982.pdf). Referência metodológica para levantamento de processos, requisitos e fluxos. O domínio de estoque do artigo não faz parte do escopo deste chatbot.

Outras referências e soluções similares serão acrescentadas após a pesquisa da equipe.
