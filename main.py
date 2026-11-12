from datetime import datetime, timezone
from threading import RLock
from typing import Literal

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="API para Fila de Atendimento",
    description="API demonstrativa para gerenciar a fila presencial de um estabelecimento.",
    version="1.0.0",
)


class ClienteEntrada(BaseModel):
    nome: str = Field(..., min_length=1, max_length=20, description="Nome do cliente (até 20 caracteres)")
    tipo: Literal["N", "P"] = Field(..., description="N para normal ou P para prioritário")

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("O nome não pode conter apenas espaços.")
        return value.strip()


class Cliente(BaseModel):
    posicao: int
    nome: str
    data_chegada: datetime
    tipo: Literal["N", "P"]
    atendido: bool


fila: list[Cliente] = []
lock = RLock()


def aguardando() -> list[Cliente]:
    return [cliente for cliente in fila if not cliente.atendido]


def reordenar_posicoes() -> None:
    for posicao, cliente in enumerate(aguardando(), start=1):
        cliente.posicao = posicao


@app.get("/fila", response_model=list[Cliente])
def listar_fila() -> list[Cliente]:
    """Lista clientes ainda não atendidos, na ordem atual de atendimento."""
    with lock:
        return aguardando()


@app.get("/fila/{id}", response_model=Cliente)
def consultar_cliente(id: int = Path(..., ge=1, description="Posição atual na fila")) -> Cliente:
    with lock:
        cliente = next((c for c in aguardando() if c.posicao == id), None)
        if cliente is None:
            raise HTTPException(status_code=404, detail=f"Não há cliente na posição {id} da fila.")
        return cliente


@app.post("/fila", response_model=Cliente, status_code=201)
def adicionar_cliente(dados: ClienteEntrada) -> Cliente:
    with lock:
        cliente = Cliente(
            posicao=0,
            nome=dados.nome,
            data_chegada=datetime.now(timezone.utc),
            tipo=dados.tipo,
            atendido=False,
        )
        fila.append(cliente)
        # Prioritários entram antes dos normais; clientes da mesma categoria
        # mantêm a ordem de chegada (FIFO).
        if dados.tipo == "P":
            primeiro_normal = next((i for i, c in enumerate(fila[:-1]) if not c.atendido and c.tipo == "N"), len(fila) - 1)
            fila.insert(primeiro_normal, fila.pop())
        reordenar_posicoes()
        return cliente


@app.put("/fila", response_model=Cliente)
def chamar_proximo() -> Cliente:
    """Atende o primeiro cliente e atualiza as posições dos demais."""
    with lock:
        proximo = next((c for c in aguardando() if c.posicao == 1), None)
        if proximo is None:
            raise HTTPException(status_code=404, detail="Não há clientes aguardando atendimento.")
        proximo.posicao = 0
        proximo.atendido = True
        reordenar_posicoes()
        return proximo


@app.delete("/fila/{id}", response_model=Cliente)
def remover_cliente(id: int = Path(..., ge=1, description="Posição atual na fila")) -> Cliente:
    with lock:
        cliente = next((c for c in aguardando() if c.posicao == id), None)
        if cliente is None:
            raise HTTPException(status_code=404, detail=f"Não há cliente na posição {id} da fila.")
        fila.remove(cliente)
        reordenar_posicoes()
        return cliente
