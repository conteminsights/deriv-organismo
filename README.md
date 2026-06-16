# Deriv Organismo

V1 do organismo autônomo para operação inicial em demo na Deriv.

## O que já existe hoje

A base atual já entrega um fluxo mínimo funcional para revisão técnica:
- especialistas de decisão por regime
- seleção via meta-agent
- score contextual e risco soberano
- execução demo protegida por `account_id`
- bloqueio explícito para execução real não promovida
- trilha auditável básica
- API operacional mínima
- worker de ciclo único
- dashboard mínimo em JSON

## O que este projeto é nesta fase

Esta V1 ainda é um bootstrap operacional, não uma mesa pronta para produção real.
Ela serve para:
- validar arquitetura
- revisar contratos internos
- testar o fluxo demo ponta a ponta
- preparar a próxima rodada de integração real

Ela ainda não serve para:
- operação real contínua sem supervisão
- promoção automática madura
- observabilidade persistente completa
- interface visual final

## Como revisar rápido

Se você quer entender o sistema sem entrar no código inteiro, siga esta ordem:

1. Ler este README
2. Abrir `docs/runbooks/local-demo.md`
3. Subir a API local
4. Ver `GET /status`
5. Ver `GET /dashboard`
6. Ver `GET /dashboard/data`
7. Rodar o worker de ciclo único
8. Revisar `docs/runbooks/promotion-readiness.md`

## Estrutura principal

- `src/deriv_organismo/services/` — regras de negócio
- `src/deriv_organismo/integrations/deriv/` — integração Deriv
- `src/deriv_organismo/workers/` — ciclo contínuo
- `src/deriv_organismo/api/` — rotas operacionais
- `src/deriv_organismo/observability/` — eventos e logging
- `docs/runbooks/` — operação local e readiness
- `tests/` — cobertura unitária e de integração

## Fluxo funcional atual

Hoje o fluxo da V1 é, em termos práticos:
1. carregar frame de mercado
2. classificar regime
3. selecionar especialistas
4. avaliar sinais
5. aplicar score contextual
6. aplicar risco soberano
7. decidir
8. executar em demo quando permitido
9. registrar eventos
10. expor estado mínimo via API

## Rotas para revisão rápida

Depois de subir a API localmente, use:
- `GET /health`
- `GET /status`
- `GET /accounts`
- `GET /events`
- `GET /decisions/latest`
- `GET /dashboard`
- `GET /dashboard/data`

## Bootstrap local

1. Instalar dependências:
   - `uv sync`
2. Criar ambiente local:
   - `cp .env.example .env`
3. Em `APP_ENV=dev`, você pode começar sem Postgres:
   - deixe `DATABASE_URL=` vazio para usar `sqlite+aiosqlite:///./deriv-organismo.db`
   - deixe `REDIS_URL=` vazio para usar `redis://localhost:6379/0`
4. Defina secrets locais de desenvolvimento:
   - `APP_SECRET_KEY`
   - `CREDENTIAL_SECRET_KEY`
5. Se quiser login master + tenant, habilite:
   - `AUTH_ENABLED=true`
   - `MASTER_EMAIL` / `MASTER_PASSWORD`
   - `TENANT_EMAIL` / `TENANT_PASSWORD` / `TENANT_SCOPE_ID`
6. Se quiser payloads live Deriv, preencha `DERIV_APP_ID`.
7. Em produção/staging, `DATABASE_URL`, `APP_SECRET_KEY` e `CREDENTIAL_SECRET_KEY` devem ser explícitos.

## Execução local

Subir a API em dev simples (SQLite local automático):
- `uv run uvicorn deriv_organismo.main:app --reload`

Se `AUTH_ENABLED=true`, autentique via `POST /login` antes de acessar as telas protegidas.

Aplicar migrations no banco configurado:
- `uv run alembic upgrade head`

Voltar para base em ambiente descartável:
- `uv run alembic downgrade base`

Rodar um ciclo único do worker:
- `uv run python scripts/run_market_loop.py`

## Testes

Suíte completa:
- `uv run pytest tests -q`

Integrações:
- `uv run pytest tests/integration -q`

Tipagem:
- `uv run mypy src`

Lint:
- `uv run ruff check .`

## Runbooks

- `docs/runbooks/local-demo.md`
- `docs/runbooks/promotion-readiness.md`

## Limites conhecidos da V1

- respostas de dashboard e parte da trilha ainda são mínimas
- há componentes com dados stubados para sustentar o fluxo
- worker ainda não é um orquestrador robusto de longa duração
- integração Deriv ainda está em estágio inicial
- não existe interface visual rica; o "dashboard" atual é JSON operacional

## Estado de segurança

A V1 está preparada para demo-first.
Execução real só pode ocorrer com promoção explícita e, quando exigido, aprovação humana.
