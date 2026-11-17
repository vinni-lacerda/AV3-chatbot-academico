# Demonstração local

Siga a [instalação do README](../README.md#instalação-e-execução). A carga fictícia prepara a atividade **Inscrições da feira** e o documento aprovado **Guia de confirmação da feira**. Use uma aba ou janela por perfil para alternar entre as contas.

1. Entre como Ada e pergunte **Como reenviar uma confirmação?**. Abra a fonte e verifique a origem e a data de 12/03/2025.
2. Entre como Lia, escolha **Registrar → Inscrições da feira → Entrevista guiada**. Na primeira resposta, informe «Abra o formulário da feira e valide a lista de inscrições». Complete os outros campos, confira o conteúdo, confirme a autorização e envie.
3. Em **Consulta**, como Ada, selecione a atividade e pergunte **Quais são as etapas?**. Enquanto o relato aguarda revisão, a resposta indica uma lacuna.
4. Entre como Beto, abra **Revisão** e expanda a versão pendente. Solicite ajustes com a observação «Detalhe quando a lista deve ser validada».
5. Como Lia, abra **Registros → Corrigir e reenviar**, edite **Etapas** para «Abra o formulário da feira e valide a lista de inscrições no fim de cada turno». Confirme a autorização novamente e reenvie.
6. Como Beto, atualize a fila e aprove a nova versão. Repita a pergunta sobre etapas como Ada e abra a fonte para conferir a versão 2, a data e a autoria.
7. Pergunte **Qual é o orçamento das inscrições da feira?**. O chatbot indica a lacuna e Beto como referência.
8. Como Beto, mude o filtro para **Aprovado** e retire a entrevista. Repita a pergunta sobre etapas para verificar a lacuna.

Para demonstrar uma substituição, crie uma nova versão de uma entrevista aprovada em **Registros**. Consulte antes e depois da aprovação da atualização. O resultado anterior fica disponível até a aprovação e sai da consulta quando a substituta entra.

## Ativar o Ollama

O modo padrão funciona localmente com busca extrativa. Para testar seleção por modelo, instale o Ollama na mesma máquina da API e baixe o modelo local `qwen2.5:3b` com `ollama pull qwen2.5:3b`. A escolha mantém o protótipo executável com um modelo pequeno e permite usar o mesmo fluxo sem contratar um provedor. Configure o serviço Ollama com `OLLAMA_NO_CLOUD=1` e execute a API diretamente no host.

Em `backend/.env`, configure:

```dotenv
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_PORT=11434
OLLAMA_TIMEOUT_SECONDS=12
```

Reinicie a API e pergunte **Como reenviar uma confirmação?**. O endpoint devolve `mode: "ollama"` quando aceita a seleção do modelo e `mode: "extractive"` quando usa o modo padrão. Se o modelo demorar a carregar, o limite pode ser ajustado no ambiente local.

Envie somente perguntas e conteúdos autorizados para o piloto. A integração usa o endpoint local de chat do Ollama. [Contrato do endpoint](https://docs.ollama.com/api/chat) · [Configuração local](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features) · [Modelo Qwen 2.5](https://ollama.com/library/qwen2.5:3b)
