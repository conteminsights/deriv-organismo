# Local demo runbook

## Objetivo

Subir e validar a V1 localmente em modo demo sem expor segredos no repositório.

## Setup local

1. Instalar dependências do projeto:
   - `uv sync`
2. Criar arquivo de ambiente:
   - `cp .env.example .env`
3. Preencher `.env` com regras seguras:
   - nunca commitar segredos
   - usar valores locais para banco e redis
   - preencher `DERIV_APP_ID` fora do git
   - futuros tokens devem ficar só no `.env`

## Subir serviços

API local:
- `uv run uvicorn deriv_organismo.main:app --reload`

Worker demo de ciclo único:
- `uv run python scripts/run_market_loop.py`

Infra local quando necessária:
- `docker compose up -d`

## Validar saúde

Rotas úteis:
- `GET /health`
- `GET /status`
- `GET /dashboard`

## Rodar testes

Suíte completa:
- `uv run pytest tests -q`

Integrações:
- `uv run pytest tests/integration -q`

## Demo-only start

Usar apenas contas com `mode=demo` até que:
- score de promoção esteja satisfatório
- guardas de real estejam verificadas
- aprovação humana exista quando requerida

## Limites conhecidos da V1

- dados e respostas ainda estão em parte stubados
- dashboard ainda é JSON mínimo
- worker ainda executa ciclo simples, não scheduler robusto
- integração Deriv ainda está em forma mínima para proposal/buy
