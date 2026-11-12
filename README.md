# API para Fila de Atendimento

API em FastAPI para simular a fila de atendimento presencial. O projeto inclui prioridade: clientes prioritários (`P`) passam à frente dos clientes normais (`N`), e a ordem de chegada é preservada dentro de cada categoria.

## Executar localmente

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

A documentação interativa fica em http://127.0.0.1:8000/docs.

## Endpoints

| Método | Rota | Ação |
| --- | --- | --- |
| GET | `/fila` | Lista os clientes aguardando. Retorna `[]` quando a fila está vazia. |
| GET | `/fila/{id}` | Consulta o cliente pela posição atual. |
| POST | `/fila` | Adiciona cliente com `nome` (1–20 caracteres) e `tipo` (`N` ou `P`). |
| PUT | `/fila` | Chama o próximo cliente, marca como atendido e reposiciona os demais. |
| DELETE | `/fila/{id}` | Remove o cliente na posição atual e reposiciona os demais. |

Erros de posição inexistente retornam HTTP 404 e um JSON com `detail` explicativo. O POST retorna HTTP 201.

