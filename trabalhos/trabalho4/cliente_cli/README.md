# CLI de teste real

Cliente Python auxiliar para testar a API em execução. Ele faz requisições
HTTP reais ao servidor e não importa seus serviços internos. Os clientes Java
e Node.js continuam sendo os clientes usados para cumprir o requisito de duas
linguagens diferentes do servidor.

No primeiro terminal, inicie API e RabbitMQ conforme o [README do Trabalho 4](../README.md).
Em outro terminal, execute:

```sh
cd trabalhos/trabalho4/cliente_cli
python3 client.py --url http://127.0.0.1:8000 --username ana
```

O menu chama catálogo, empréstimos e notificações do servidor. A opção 8 lista
os usuários e papéis; opção 9 inscreve o cliente no canal HTTP; opção 10
consulta eventos posteriores ao cursor; opção 11 cancela a inscrição. A URL e
o nome também aceitam `API_URL` e `LIBRARY_USERNAME`.

Para usar o menu em outra máquina, troque `127.0.0.1` pelo IP LAN do servidor,
por exemplo `--url http://192.168.1.20:8000`. Inscreva o primeiro cliente com a
opção 9, faça uma operação de catálogo/empréstimo em outro cliente e consulte
as notificações com a opção 10.

Para verificar o fluxo HTTP sem navegar pelo menu:

```sh
python3 client.py --url http://127.0.0.1:8000 --username teste --smoke-test
```

O smoke test cadastra um livro, solicita um empréstimo, devolve-o, valida os
papéis Leitor/Bibliotecário e consulta os eventos pela inscrição HTTP. O livro
e o empréstimo devolvido permanecem na memória até o servidor reiniciar. O
RabbitMQ precisa estar ativo porque o servidor publica eventos durante o fluxo.
