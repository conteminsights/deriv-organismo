# Deriv Organismo

V1 do organismo autônomo para operação inicial em demo na Deriv.

## Objetivo

Fechar uma base funcional para:
- leitura de mercado
- decisão por especialistas
- risco soberano
- execução demo isolada por conta
- trilha auditável
- API operacional mínima

## Estrutura principal

- `src/deriv_organismo/services/` — regras de negócio
- `src/deriv_organismo/integrations/deriv/` — integração Deriv
- `src/deriv_organismo/workers/` — ciclo contínuo
- `src/deriv_organismo/api/` — rotas operacionais
- `src/deriv_organismo/observability/` — eventos e logging
- `docs/runbooks/` — operação local e readiness

## Bootstrap local

1. Criar/usar o ambiente do projeto:
   - `uv sync`
2. Copiar a base de ambiente:
   - `cp .env.example .env`
3. Preencher `.env` sem commitar segredos:
   - URLs locais de Postgres/Redis
   - `DERIV_APP_ID`
   - futuros tokens fora do repositório

## Execução local

Subir a API:
- `uv run uvicorn deriv_organismo.main:app --reload`

Rodar um ciclo único do worker:
- `uv run python scripts/run_market_loop.py`

## Testes

Rodar suíte completa:
- `uv run pytest tests -q`

Rodar integração específica:
- `uv run pytest tests/integration -q`

## Runbooks

- `docs/runbooks/local-demo.md`
- `docs/runbooks/promotion-readiness.md`

## Escopo atual da V1

A V1 está preparada para demo-first. Execução real só pode ocorrer com promoção explícita e, quando exigido, aprovação humana.
