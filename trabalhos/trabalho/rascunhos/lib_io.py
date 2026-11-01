import io

# Testes feitos para aprender usar stream1


# StringIO -> (strings)
#   texto claro em memoria 
# 
# Fica na memoria RAM

stream = io.StringIO()
stream.write("Olá ")
stream.write("Calebe ")
print(stream.getvalue())

# Bytes em memoria
# Trabalha com Bytes
#
# Fica na memoria RAM
stream = io.BytesIO()
stream.write(b"ABC")
print(stream.getvalue())

arquivo = io.open("teste.txt", "w")
arquivo.write("Olá mundo kska")
arquivo.close()


# RawIOBase é uma classe base apra streams de baixo nivel
# criamos a classe
# e colocamos como paremeto io.RawIOBase
#
# write por exemplo Trabalha e Bytes
#
# por isso usamos
# stream.write(b"Testo para bytes")