# Relatório — Trabalho 2: RPC/RMI

## Identificação

Disciplina: Sistemas Distribuídos — UFC, Campus de Quixadá

**Integrantes:** [PREENCHER]

**Repositório:** [PREENCHER URL DO GITHUB]

## 1. Objetivo

Reimplementar o serviço de notificações de uma biblioteca em uma arquitetura cliente-servidor de requisição-resposta, usando RPC como alternativa à comunicação diretamente baseada em sockets do Trabalho 1.

## 2. Implementação

Foi utilizado Python e a infraestrutura XML-RPC da biblioteca padrão, sem criação manual de sockets no código da aplicação. Uma mensagem de aplicação em JSON UTF-8 é transmitida como argumento binário de uma chamada XML-RPC. As mensagens incluem `messageType`, `requestId`, `objectReference`, `methodId` e `arguments`, em conformidade conceitual com a Figura 5.4 de Coulouris.

O cliente implementa `doOperation`, o servidor implementa `getRequest` e `sendReply` com assinaturas adaptadas. O método remoto de transporte `exchange` encaminha cada requisição ao objeto correspondente e devolve a resposta.

## 3. Modelo de objetos

Herança: `Leitor` e `Bibliotecario` derivam de `Usuario`; `Alerta` e `Atualizacao` derivam de `Notificacao`.

Agregações: `Biblioteca` contém `Catalogo` e `HistoricoEmprestimos`; `CanalNotificacoes` contém `Inscricoes` e uma coleção de notificações.

Métodos disponíveis via RPC: cadastro/listagem/empréstimo/devolução de livros, inscrição/cancelamento/consulta/publicação de notificações e obtenção da referência de um canal remoto.

## 4. Passagem por valor e referência

Por valor: os dados de um livro são enviados em JSON UTF-8 e reconstruídos no servidor como entidade `Livro`.

Por referência: `obter_canal` retorna o identificador global do objeto remoto `notificacoes`, que é encapsulado em um `RemoteProxy` local. As operações seguintes executam no objeto do servidor. Trata-se de um modelo de referência remota implementado na aplicação, não de um objeto Java RMI.

## 5. Adaptação do multicast

A questão 4 do Trabalho 1 previa multicast UDP real. Para atender à restrição de utilizar apenas RPC/RMI e não criar sockets, esta solução substitui o multicast IP por distribuição lógica de eventos: vários clientes se registram no canal e consultam periodicamente novas mensagens por RPC. O uso de *polling* preserva a entrega do mesmo evento a diversos clientes, mas não implementa multicast de rede. **A aceitação dessa adaptação deve ser confirmada com o professor.**

## 6. Tratamento de repetição

Cada mensagem possui um `requestId`. O despachante mantém respostas recentes em uma cache limitada, que permite devolver o mesmo resultado caso uma requisição seja repetida com o mesmo identificador. Isso demonstra filtragem de duplicatas, sem garantir persistência ou semântica no-máximo-uma-vez após reinícios.

## 7. Testes

Execute `python -m unittest discover -s tests -v` e registre o resultado de cada caso. Os testes verificam herança, referência remota, serialização, difusão lógica para dois clientes, métodos remotos, deduplicação e validação de mensagens.

**Evidências a anexar:** [CAPTURA DO SERVIDOR], [CAPTURA DE DOIS CLIENTES], [CAPTURA DO PUBLICADOR], [CAPTURA DOS TESTES].

## 8. Limitações e conclusão

O serviço é demonstrativo e textual, armazena dados em memória, não autentica usuários e não realiza multicast UDP real. A aplicação demonstra a organização de um protocolo de requisição-resposta sobre RPC, a representação externa JSON, múltiplos métodos remotos, herança, agregação e uso de referências remotas.
