import json
import struct


def main(caminho: str = "saida.bin") -> None:
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()

    posicao = 0
    objetos = []
    while posicao < len(dados):
        if len(dados) - posicao < 4:
            raise EOFError("cabeçalho incompleto no arquivo")
        tamanho = struct.unpack(">I", dados[posicao:posicao + 4])[0]
        posicao += 4
        fim = posicao + tamanho
        if fim > len(dados):
            raise EOFError("JSON incompleto no arquivo")
        objetos.append(json.loads(dados[posicao:fim].decode("utf-8")))
        posicao = fim

    print(f"Total: {len(dados)} bytes")
    for indice, objeto in enumerate(objetos, 1):
        print(f"Objeto {indice}: {objeto}")
    print(f"\n{len(objetos)} objetos lidos com sucesso")


if __name__ == "__main__":
    main()
