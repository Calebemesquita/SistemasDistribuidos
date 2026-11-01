"""Servidor XML-RPC; não instancia sockets diretamente no código do projeto."""
from collections import OrderedDict
from threading import RLock
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import Binary

from .entities import Biblioteca, CanalNotificacoes
from .protocol import decode_json, make_reply, payload


class RPCDispatcher:
    def __init__(self):
        self.canal = CanalNotificacoes()
        self.biblioteca = Biblioteca(self.canal)
        self._objects = {"biblioteca": self.biblioteca, "notificacoes": self.canal}
        self._allowed = {
            "biblioteca": {"cadastrar_livro", "listar_livros", "emprestar_livro", "devolver_livro", "obter_canal"},
            "notificacoes": {"inscrever", "cancelar_inscricao", "publicar", "consultar"},
        }
        self._historico = OrderedDict()
        self._lock = RLock()

    def getRequest(self, raw: bytes) -> dict:
        request = decode_json(raw)
        keys = {"messageType", "requestId", "objectReference", "methodId", "arguments"}
        if not isinstance(request, dict) or not keys.issubset(request) or request["messageType"] != "Request":
            raise ValueError("Formato de requisição inválido")
        if not isinstance(request["arguments"], list):
            raise ValueError("Argumentos inválidos")
        return request

    def sendReply(self, response: bytes) -> Binary:
        return Binary(response)

    def exchange(self, request_binary: Binary) -> Binary:
        """Entrada remota única: cada chamada entrega uma requisição e recebe uma resposta."""
        request = self.getRequest(request_binary.data)
        key = str(request["requestId"])
        with self._lock:
            if key in self._historico:
                return self.sendReply(self._historico[key])
            try:
                ref, method = request["objectReference"], request["methodId"]
                if method not in self._allowed.get(ref, set()):
                    raise ValueError("Objeto ou método remoto desconhecido")
                if ref == "biblioteca" and method == "obter_canal":
                    result = {"__remote_ref__": "notificacoes"}
                else:
                    kwargs = payload(request)
                    if not isinstance(kwargs, dict):
                        raise ValueError("Argumentos devem ser um objeto JSON")
                    result = getattr(self._objects[ref], method)(**kwargs)
                response = make_reply(request, result=result)
            except (ValueError, TypeError) as exc:
                response = make_reply(request, error=str(exc))
            self._historico[key] = response
            # Limite de memória para demonstração. Não garante deduplicação para sempre.
            if len(self._historico) > 2048:
                self._historico.popitem(last=False)
            return self.sendReply(response)


def main():
    dispatcher = RPCDispatcher()
    with SimpleXMLRPCServer(("127.0.0.1", 8765), allow_none=True, logRequests=False) as server:
        server.register_function(dispatcher.exchange, "exchange")
        print("Servidor RPC ativo em http://127.0.0.1:8765")
        print("Objetos remotos: biblioteca, notificacoes")
        server.serve_forever()


if __name__ == "__main__":
    main()
