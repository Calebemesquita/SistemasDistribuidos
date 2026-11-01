"""Cliente com proxy local de referência remota e doOperation."""
from xmlrpc.client import Binary, ServerProxy

from .protocol import decode_json, make_request, payload


class RPCError(RuntimeError):
    pass


class RPCClient:
    def __init__(self, url="http://127.0.0.1:8765"):
        self._transport = ServerProxy(url, allow_none=True)

    def doOperation(self, remote_object_ref: str, method_id: str, arguments: bytes) -> bytes:
        """Envia Request e retorna Reply, ambos como sequências de bytes."""
        kwargs = decode_json(arguments)
        request = make_request(remote_object_ref, method_id, kwargs)
        reply: Binary = self._transport.exchange(Binary(request))
        msg = decode_json(reply.data)
        if msg.get("requestId") != decode_json(request)["requestId"] or msg.get("messageType") != "Reply":
            raise RPCError("Resposta não corresponde à requisição")
        return reply.data

    def object(self, remote_ref="biblioteca"):
        return RemoteProxy(self, remote_ref)


class RemoteProxy:
    """Referência remota local; não contém o objeto do servidor."""
    def __init__(self, client: RPCClient, remote_ref: str):
        self._client = client
        self.remote_ref = remote_ref

    def call(self, method: str, **kwargs):
        from .protocol import encode_json
        result_bytes = self._client.doOperation(self.remote_ref, method, encode_json(kwargs))
        reply = payload(decode_json(result_bytes))
        if reply["error"] is not None:
            raise RPCError(reply["error"])
        result = reply["result"]
        if isinstance(result, dict) and "__remote_ref__" in result:
            return RemoteProxy(self._client, result["__remote_ref__"])
        return result
