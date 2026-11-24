"""Protocolo request-reply explicitamente serializado em JSON UTF-8."""
import json
from uuid import uuid4


def encode_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def decode_json(data: bytes):
    return json.loads(data.decode("utf-8"))


def make_request(object_ref: str, method_id: str, arguments: dict, request_id: str | None = None) -> bytes:
    return encode_json({
        "messageType": "Request", "requestId": request_id or uuid4().hex,
        "objectReference": object_ref, "methodId": method_id,
        "arguments": list(encode_json(arguments)),
    })


def make_reply(request: dict, *, result=None, error: str | None = None) -> bytes:
    return encode_json({
        "messageType": "Reply", "requestId": request["requestId"],
        "objectReference": request["objectReference"],
        "methodId": request["methodId"],
        "arguments": list(encode_json({"result": result, "error": error})),
    })


def payload(message: dict):
    return decode_json(bytes(message["arguments"]))
