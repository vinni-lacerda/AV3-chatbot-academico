# Demonstração local

Siga a [instalação do README](../README.md#instalação-e-execução). Se você já tem a base de demonstração, execute novamente a etapa `python -m infrastructure.persistence.demo` no mesmo ambiente para acrescentar os exemplos fictícios.

## Apresentação rápida

Entre com `ada@demo.example`, abra **Consulta** e selecione a atividade correspondente antes de enviar cada pergunta. As seis perguntas abaixo já têm fontes aprovadas e podem ser apresentadas na mesma sessão da Ada.

### Rotinas do diretório acadêmico

Ada chegou ao diretório e precisa assumir atividades da gestão anterior.

| Atividade | Pergunta | O que mostrar |
| --- | --- | --- |
| Credenciamento do evento de tecnologia | O que fazer se o QR code falhar? | O guia orienta conferir o nome e o e-mail e registrar a presença manualmente. |
| Reserva de salas | Como solicitar uma sala? | O procedimento explica o que informar à secretaria e quando divulgar o local. |
| Encaminhamento de demandas estudantis | Como reiterar o pedido? | O roteiro explica como conferir o protocolo e dar retorno ao estudante. |

### Manutenção do Portal Atlas

No **Portal Atlas**, um software estudantil fictício, Lia está passando a manutenção das notificações para Ada. Ela precisa entender como rodar o sistema, como o código está organizado e por que uma decisão técnica foi tomada.

| Atividade | Pergunta | O que mostrar |
| --- | --- | --- |
| Ambiente local do Portal Atlas | Como iniciar a API localmente? | O guia lista configuração, banco de desenvolvimento, migrações e checagem de saúde da API. Abra a fonte para mostrar a origem e a data. |
| Manutenção de notificações do Portal Atlas | Por que o envio de notificações usa uma fila? | O registro explica o fluxo entre a API, a fila e o worker, e por que o envio de e-mail foi separado da inscrição. |
| Manutenção de notificações do Portal Atlas | Como reprocessar notificações? | O procedimento explica como localizar a mensagem, verificar o status `FAILED`, reenfileirar e acompanhar o envio. |

## Teste opcional de registro e revisão

Use perfis de navegador separados para manter as sessões de Ada, Lia e Beto abertas ao mesmo tempo.

1. Como Lia, escolha **Registrar → Manutenção de notificações do Portal Atlas → Entrevista guiada**. Use as respostas de exemplo abaixo, confira o conteúdo, confirme a autorização e envie.
2. Como Ada, selecione a atividade em **Consulta** e pergunte **Como identificar notificações duplicadas?**. Enquanto o relato aguarda revisão, a pergunta continua sem resposta aprovada.
3. Como Beto, expanda a versão pendente em **Revisão** e solicite ajustes com a observação «Informe quais tentativas devem ser comparadas».
4. Como Lia, abra **Registros → Corrigir e reenviar** e acrescente às **Etapas** «Compare apenas tentativas com status `SENT` para a mesma inscrição». Confirme a autorização e reenvie.
5. Como Beto, aprove a nova versão. Como Ada, repita a pergunta e abra a fonte para conferir a versão 2, a data e a autoria.
6. Como Beto, use o filtro **Aprovado** em **Revisão** e retire a entrevista. Repita a pergunta em **Consulta** para verificar a lacuna.

| Campo da entrevista | Resposta fictícia para copiar |
| --- | --- |
| Etapas | Para identificar notificações duplicadas, localize o identificador da inscrição no painel da fila e compare o histórico de tentativas. |
| Recursos | Painel da fila e logs do worker no ambiente de desenvolvimento. |
| Dificuldades | Às vezes o provedor de e-mail fica indisponível e a mensagem acumula tentativas com erro. |
| Soluções | Espere a recuperação do provedor e acompanhe a atualização do status no painel. |
| Decisões | O worker foi separado da API para que a inscrição termine mesmo quando o provedor demora. |
| Recomendações | Teste o fluxo com uma inscrição fictícia antes de alterar o worker. |

Para demonstrar uma substituição, crie uma nova versão de uma entrevista aprovada em **Registros**. Consulte antes e depois da aprovação da atualização. O resultado anterior fica disponível até a aprovação e sai da consulta quando a substituta entra.

## Ativar o Ollama

O modo padrão funciona localmente com busca extrativa. Para testar seleção por modelo, instale o Ollama na mesma máquina da API e baixe o modelo local `qwen2.5:3b` com `ollama pull qwen2.5:3b`. A escolha mantém o protótipo executável com um modelo pequeno e permite usar o mesmo fluxo sem contratar um provedor. Configure o serviço Ollama com `OLLAMA_NO_CLOUD=1` e execute a API diretamente no host.

Em `backend/.env`, configure:

```dotenv
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_PORT=11434
OLLAMA_TIMEOUT_SECONDS=12
```

Reinicie a API, selecione **Manutenção de notificações do Portal Atlas** e pergunte **Por que o envio de notificações usa uma fila?**. O endpoint devolve `mode: "ollama"` quando aceita a seleção do modelo e `mode: "extractive"` quando usa o modo padrão. Se o modelo demorar a carregar, o limite pode ser ajustado no ambiente local.

Envie somente perguntas e conteúdos autorizados para o piloto. A integração usa o endpoint local de chat do Ollama. [Contrato do endpoint](https://docs.ollama.com/api/chat) · [Configuração local](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features) · [Modelo Qwen 2.5](https://ollama.com/library/qwen2.5:3b)
