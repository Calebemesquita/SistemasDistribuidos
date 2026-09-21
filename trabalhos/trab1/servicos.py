"""
Classes de serviço do Sistema de Votação Distribuída.

O enunciado pede "2 classes de serviço que implementam operações" sobre os
POJOs do domínio. Aqui ficam as duas:

- ServicoVotacao: operações usadas pelos eleitores (login, listar
  candidatos, votar, apurar resultado).
- ServicoAdministracao: operações usadas pelos administradores (login,
  adicionar/remover candidato, montar uma nota informativa, encerrar a
  votação antes do prazo).

Este módulo é só a LÓGICA DE NEGÓCIO, sem nenhuma dependência de socket ou
de rede: quem usa isso (serializacao/, multicast/, votacao/) é responsável
por receber a requisição, chamar o método certo daqui e empacotar a
resposta. Isso deixa a lógica testável isoladamente (ver tests/test_servicos.py)
e reaproveitável nas diferentes fases do trabalho.

Como vários clientes (threads) podem chamar os mesmos métodos ao mesmo
tempo (ex.: dois eleitores votando no mesmo instante), o estado é protegido
por um threading.RLock.
"""
import threading
import time
from typing import Dict, List, Optional

from common.pojos import Candidato, Eleitor, NotaInformativa, Voto


class ErroServico(Exception):
    """Erro de negócio (login inválido, eleitor já votou, votação encerrada etc.)."""


class ServicoVotacao:
    """Operações do lado do eleitor sobre o estado da votação."""

    def __init__(
        self,
        candidatos: Optional[List[Candidato]] = None,
        duracao_segundos: Optional[float] = None,
    ):
        self._lock = threading.RLock()
        self.candidatos: Dict[int, Candidato] = {c.id: c for c in (candidatos or [])}
        self.eleitores: Dict[str, Eleitor] = {}  # chave = título de eleitor
        self.votos: List[Voto] = []
        self.inicio = time.time()
        self.duracao_segundos = duracao_segundos  # None = sem prazo definido
        self._encerrada_manualmente = False
        self._resultado_cache: Optional[dict] = None

    # --- controle de prazo -------------------------------------------------
    def votacao_aberta(self) -> bool:
        with self._lock:
            if self._encerrada_manualmente:
                return False
            if self.duracao_segundos is None:
                return True
            return (time.time() - self.inicio) < self.duracao_segundos

    def tempo_restante(self) -> float:
        with self._lock:
            if self.duracao_segundos is None:
                return float("inf")
            return max(0.0, self.duracao_segundos - (time.time() - self.inicio))

    def encerrar(self) -> None:
        """Encerra a votação (chamado pelo temporizador ou por um admin)."""
        with self._lock:
            self._encerrada_manualmente = True

    # --- operações do eleitor ----------------------------------------------
    def login_eleitor(self, titulo: str, nome: str) -> Eleitor:
        if not titulo or not nome:
            raise ErroServico("Título de eleitor e nome são obrigatórios")
        with self._lock:
            eleitor = self.eleitores.get(titulo)
            if eleitor is None:
                eleitor = Eleitor(id=len(self.eleitores) + 1, nome=nome, titulo=titulo)
                self.eleitores[titulo] = eleitor
            return eleitor

    def listar_candidatos(self) -> List[Candidato]:
        with self._lock:
            return list(self.candidatos.values())

    def votar(self, titulo_eleitor: str, id_candidato: int) -> Voto:
        with self._lock:
            if not self.votacao_aberta():
                raise ErroServico("Votação encerrada: prazo esgotado")
            eleitor = self.eleitores.get(titulo_eleitor)
            if eleitor is None:
                raise ErroServico("Eleitor não autenticado; faça login primeiro")
            if eleitor.ja_votou:
                raise ErroServico("Eleitor já votou")
            candidato = self.candidatos.get(id_candidato)
            if candidato is None:
                raise ErroServico(f"Candidato {id_candidato} não existe")

            voto = Voto(
                id_eleitor=eleitor.id,
                id_candidato=id_candidato,
                timestamp=int(time.time()),
            )
            self.votos.append(voto)
            candidato.votos += 1
            eleitor.ja_votou = True
            return voto

    # --- apuração ------------------------------------------------------------
    def calcular_resultado(self, forcar: bool = False) -> dict:
        """
        Calcula total de votos, percentual por candidato e o vencedor.
        Só apura de fato quando a votação está fechada (prazo esgotado ou
        encerrada manualmente) — exatamente como pede o enunciado da questão
        extra ("finalizado esse tempo... calcula o total de votos"). Antes
        disso, sinaliza que a apuração ainda não está disponível.
        `forcar=True` é usado internamente pelo temporizador do servidor.
        """
        with self._lock:
            if not forcar and self.votacao_aberta():
                raise ErroServico("Votação ainda em andamento; resultado não disponível")

            if self._resultado_cache is not None:
                return self._resultado_cache

            total = len(self.votos)
            candidatos = list(self.candidatos.values())
            resultados = [
                {
                    "candidato": c.to_dict(),
                    "percentual": round((c.votos / total * 100), 2) if total else 0.0,
                }
                for c in candidatos
            ]
            resultados.sort(key=lambda r: r["candidato"]["votos"], reverse=True)

            vencedor = None
            empate = False
            if candidatos:
                maior = max(c.votos for c in candidatos)
                empatados = [c for c in candidatos if c.votos == maior]
                if maior > 0 and len(empatados) == 1:
                    vencedor = empatados[0].to_dict()
                elif len(empatados) > 1:
                    empate = True

            resultado = {
                "total_votos": total,
                "resultados": resultados,
                "vencedor": vencedor,
                "empate": empate,
            }
            self._resultado_cache = resultado
            return resultado


class ServicoAdministracao:
    """Operações do lado do administrador: gerência de candidatos e notas."""

    def __init__(self, servico_votacao: ServicoVotacao, senha: str = "admin123"):
        self._servico_votacao = servico_votacao
        self._senha = senha
        self._lock = threading.RLock()
        self._proximo_id = max(servico_votacao.candidatos.keys(), default=0) + 1

    def login_admin(self, usuario: str, senha: str) -> bool:
        if senha != self._senha:
            raise ErroServico("Usuário/senha de administrador inválidos")
        return True

    def adicionar_candidato(self, nome: str, partido: str) -> Candidato:
        if not nome or not partido:
            raise ErroServico("Nome e partido são obrigatórios")
        with self._lock:
            candidato = Candidato(id=self._proximo_id, nome=nome, partido=partido)
            self._servico_votacao.candidatos[candidato.id] = candidato
            self._proximo_id += 1
            return candidato

    def remover_candidato(self, id_candidato: int) -> None:
        with self._lock:
            if id_candidato not in self._servico_votacao.candidatos:
                raise ErroServico(f"Candidato {id_candidato} não existe")
            del self._servico_votacao.candidatos[id_candidato]

    def encerrar_votacao(self) -> None:
        self._servico_votacao.encerrar()

    def montar_nota(self, tipo: str, mensagem: str) -> NotaInformativa:
        tipos_validos = {"NOTIFICACAO", "ALERTA", "ATUALIZACAO"}
        if tipo not in tipos_validos:
            raise ErroServico(f"Tipo de nota inválido: {tipo} (use {tipos_validos})")
        return NotaInformativa(tipo=tipo, mensagem=mensagem, timestamp=int(time.time()))
