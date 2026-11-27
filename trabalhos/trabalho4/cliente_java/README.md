# Cliente Java

Cliente de terminal independente para a API do Trabalho 4. Requer JDK 11 ou
mais recente.

```sh
javac Client.java
java Client http://HOST_DO_SERVIDOR:8000 ana
```

O primeiro argumento é a URL da API e o segundo é o nome do cliente. Esse nome
é usado como `Leitor` nos empréstimos e como `Bibliotecario` ao cadastrar
livros.
