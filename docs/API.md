# Referência da API

Base local: `http://127.0.0.1:8000`

Abra `http://127.0.0.1:8000/docs` para explorar e executar as operações pela interface do FastAPI.

## Modelo de cliente

```json
{
  "posicao": 1,
  "nome": "Ana",
  "data_chegada": "2026-11-12T15:30:00Z",
  "tipo": "N",
  "atendido": false
}
```

`tipo` é `N` (normal) ou `P` (prioritário). `data_chegada` é uma data e hora ISO 8601 em UTC. As posições dos clientes que aguardam começam em 1. Quando atendido, o cliente passa para a posição 0 e deixa de aparecer nas consultas da fila.

## `GET /fila`

Retorna todos os clientes ainda não atendidos na ordem de atendimento. Se estiver vazia, retorna HTTP 200 com `[]`.

## `GET /fila/{id}`

Consulta o cliente na posição atual indicada por `id` (inteiro maior ou igual a 1).

- Sucesso: HTTP 200 e o objeto do cliente.
- Posição inexistente: HTTP 404.

```json
{"detail":"Não há cliente na posição 8 da fila."}
```

## `POST /fila`

Adiciona um cliente. Nome deve conter de 1 a 20 caracteres e não pode ser apenas espaços. Tipo aceita somente `N` ou `P`.

```json
{"nome":"Ana","tipo":"N"}
```

Retorna HTTP 201 e o registro criado. Clientes prioritários são inseridos antes dos normais; a ordem de chegada é mantida entre clientes da mesma categoria.

## `PUT /fila`

Chama o próximo cliente da fila: marca `atendido` como `true`, define sua posição como 0 e atualiza as posições dos demais. Retorna o cliente chamado com HTTP 200. Se não houver clientes aguardando, retorna HTTP 404 com `detail` explicativo.

## `DELETE /fila/{id}`

Remove o cliente que ocupa a posição atual indicada. Os demais clientes são reposicionados. Retorna o cliente removido com HTTP 200. Se a posição não existir, retorna HTTP 404 com `detail` explicativo.

## Validação de entrada

Corpos inválidos, como nome acima do limite ou tipo diferente de `N`/`P`, recebem HTTP 422 com detalhes dos campos inválidos no padrão do FastAPI.

## Exemplos com cURL

```bash
curl http://127.0.0.1:8000/fila
curl -X POST http://127.0.0.1:8000/fila -H "Content-Type: application/json" -d '{"nome":"Ana","tipo":"N"}'
curl http://127.0.0.1:8000/fila/1
curl -X PUT http://127.0.0.1:8000/fila
curl -X DELETE http://127.0.0.1:8000/fila/1
```

## Limitação desta versão

O armazenamento é em memória. Reiniciar o processo limpa os dados; múltiplas instâncias não compartilham a mesma fila. Para produção, use um banco compartilhado e controle transacional das operações da fila.
