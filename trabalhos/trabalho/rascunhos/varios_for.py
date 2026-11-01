emails_pendentes = ["Ana@z.com", "bruno@gmail", "carlos@thiago", "calebemesquita@gmail"]
limite = 3
print("Iniciando os envios")

for i in range(min(limite, len(emails_pendentes))):
    current_email = emails_pendentes[i]
    print(f" Email -> {current_email}")

print("Finish")



carrinho = [15.00, 25.50, 10.00, 50.00, 100.00, 30.00]
quantidade_que_vou_levar = 4

total = 0

for i in range(min(quantidade_que_vou_levar, len(carrinho))):
    preco = carrinho[i]
    total += preco
    print(f"Passou item {i+1} de RS {preco:.2f}")

print(f"Total {total:.2f}")
