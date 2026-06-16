# Local demo runbook

## Objetivo

Subir e validar a V1 localmente em modo demo, sem expor segredos no repositório, e entender o que olhar primeiro na interface operacional atual.

## Antes de começar

Este projeto ainda está em fase bootstrap.
O objetivo aqui não é provar produção; é revisar:
- se a API sobe
- se as rotas mínimas respondem
- se o fluxo demo básico está coerente
- se a documentação e os contratos fazem sentido

## Setup local

1. Instalar dependências:
   - `uv sync`
2. Criar arquivo de ambiente:
   - `cp .env.example .env`
3. Para começar rápido em `APP_ENV=dev`:
   - pode deixar `DATABASE_URL=` vazio e usar SQLite local automático
   - pode deixar `REDIS_URL=` vazio e usar `redis://localhost:6379/0`
4. Se quiser validar com Postgres/Redis locais desde já:
   - preencher `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/deriv_organismo`
   - preencher `REDIS_URL=redis://localhost:6379/0`
5. Em `prod`/`staging`, `DATABASE_URL` deve ser explícito.
6. Preencher `DERIV_APP_ID` fora do git.

## Subir infraestrutura

Quando quiser rodar com Postgres e Redis locais:
- `docker compose up -d`

Checar containers:
- `docker compose ps`

Aplicar migrations no banco configurado:
- `uv run alembic upgrade head`

## Subir a API

Comando:
- `uv run uvicorn deriv_organismo.main:app --reload`

Endereço padrão esperado:
- `http://127.0.0.1:8000`

## O que abrir primeiro

Para revisão humana rápida, use esta ordem:

1. `GET /health`
   - prova que a API subiu
2. `GET /status`
   - mostra status operacional mínimo
3. `GET /dashboard`
   - visão agregada visual da V1 atual
4. `GET /dashboard/data`
   - payload bruto do painel para inspeção operacional
5. `GET /events`
   - trilha de eventos mínima
6. `GET /decisions/latest`
   - último artefato de decisão exposto

## Como abrir no navegador

Exemplos:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/status`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/dashboard/data`

## Rodar worker demo de ciclo único

Comando:
- `uv run python scripts/run_market_loop.py`

Uso esperado:
- validar o encadeamento mínimo entre decisão, execução demo e evento de ciclo

## Rodar testes

Suíte completa:
- `uv run pytest tests -q`

Somente integrações:
- `uv run pytest tests/integration -q`

Tipagem:
- `uv run mypy src`

Lint:
- `uv run ruff check .`

## Demo-only start

Usar apenas contas com `mode=demo` até que:
- score de promoção esteja satisfatório
- guardas de real estejam verificadas
- aprovação humana exista quando requerida
- a integração real com Deriv esteja endurecida

## O que você vai ver hoje

Hoje a interface já tem uma camada visual mínima.
O endpoint `/dashboard` agora entrega uma página HTML operacional, útil para revisar:
- status da aplicação
- conta principal
- última decisão
- blocos de risco
- promoções recentes

Se você quiser o payload bruto, use `/dashboard/data`.

## Limites conhecidos da V1

- dados e respostas ainda estão em parte stubados
- dashboard ainda é visual mínimo, não painel final
- worker ainda executa ciclo simples, não scheduler robusto
- integração Deriv ainda está em forma mínima para proposal/buy
- parte da observabilidade ainda não está persistida em banco
