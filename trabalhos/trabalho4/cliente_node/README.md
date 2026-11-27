# Cliente Node.js

Cliente de terminal independente para a API do Trabalho 4. Requer Node.js 18
ou mais recente e npm.

```sh
npm install
npm start -- http://HOST_DO_SERVIDOR:8000 bruno
```

Defina `RABBITMQ_URL` para conectar a um broker acessível. Use a opção 8 do
menu para assinar as notificações e a opção 9 para cancelar a assinatura.
O nome passado como segundo argumento identifica o `Leitor` nos empréstimos e
o `Bibliotecario` que cadastra livros.
