from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.services import get_library
from api.models.user import UserResponse
from biblioteca_rpc.entities import Bibliotecario, Biblioteca, Leitor, serializar

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/", response_model=list[UserResponse], name="List registered users")
def list_users(library: Annotated[Biblioteca, Depends(get_library)]) -> list[dict]:
    users = []
    for user in library.listar_usuarios():
        data = serializar(user)
        role = "bibliotecario" if isinstance(user, Bibliotecario) else "leitor"
        if not isinstance(user, (Bibliotecario, Leitor)):
            role = "usuario"
        users.append({"id": data["identificador"], "name": data["nome"], "role": role})
    return users
