# Deriv Organismo V1 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Construir a V1 do organismo autônomo Deriv com operação inicial em demo, arquitetura preparada para evolução multi-tenant/multi-conta, especialistas por regime, risco soberano e trilha auditável.

**Architecture:** O sistema será um backend Python modular com um núcleo de orquestração de mercado, integração WebSocket/REST com a Deriv, motor de especialistas interpretáveis, meta-agente de seleção, camada soberana de risco, memória operacional e laboratório evolutivo em demo. A V1 roda para um operador principal, mas todas as entidades críticas já nascem account-aware para suportar múltiplas contas/API no futuro sem refatoração estrutural.

**Tech Stack:** Python 3.12, uv, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL, Redis, websockets/httpx, scikit-learn, pandas, numpy, structlog, pytest, pytest-asyncio, Docker Compose.

---

## Pré-condições e convenções

### Estrutura alvo do repositório

```text
/home/alexandre/projetos/deriv-organismo/
  pyproject.toml
  uv.lock
  .env.example
  docker-compose.yml
  Dockerfile
  Makefile
  README.md
  docs/
    superpowers/specs/2026-06-15-deriv-organismo-v1-design.md
    plans/2026-06-15-deriv-organismo-v1-implementation-plan.md
  src/deriv_organismo/
    main.py
    config.py
    db/
    domain/
    services/
    integrations/deriv/
    workers/
    api/
    observability/
  tests/
    unit/
    integration/
    e2e/
  scripts/
```

### Convenções obrigatórias

- Todas as tabelas de negócio precisam de `account_id`, mesmo na V1 single-operator.
- Toda chamada para a Deriv deve passar por um `AccountContext` explícito.
- Nenhuma estratégia acessa credenciais diretamente.
- Risco soberano roda antes de qualquer execução.
- Toda decisão importante gera evento persistido.
- TDD em tudo que cria regra de negócio.

### Endpoints Deriv que a V1 deve cobrir

- Market data: `active_symbols`, `ticks_history`, `ticks`
- System: `ping`, `time`, `trading_times`
- Trading: `proposal`, `buy`, `proposal_open_contract`, `sell` (quando aplicável)
- Account/monitoring: `balance`, `portfolio`, `transaction`

---

## Task 1: Inicializar o repositório Python

**Objective:** Criar a base executável do projeto com ferramentas, diretórios e arquivos raiz.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/pyproject.toml`
- Create: `/home/alexandre/projetos/deriv-organismo/.python-version`
- Create: `/home/alexandre/projetos/deriv-organismo/.gitignore`
- Create: `/home/alexandre/projetos/deriv-organismo/README.md`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/__init__.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/main.py`
- Create: `/home/alexandre/projetos/deriv-organismo/tests/__init__.py`

**Step 1: Write failing test**

Create `tests/unit/test_project_boot.py`:

```python
from deriv_organismo.main import create_app


def test_create_app_exposes_health_route():
    app = create_app()
    routes = {route.path for route in app.routes}
    assert "/health" in routes
```

**Step 2: Run test to verify failure**

Run: `cd /home/alexandre/projetos/deriv-organismo && pytest tests/unit/test_project_boot.py -v`
Expected: FAIL — module or function missing.

**Step 3: Write minimal implementation**

Create `src/deriv_organismo/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Deriv Organismo")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

Use this `pyproject.toml` baseline:

```toml
[project]
name = "deriv-organismo"
version = "0.1.0"
description = "Organismo autônomo Deriv V1"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.8",
  "pydantic-settings>=2.4",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "asyncpg>=0.29",
  "redis>=5.0",
  "httpx>=0.27",
  "websockets>=12.0",
  "structlog>=24.4",
  "pandas>=2.2",
  "numpy>=2.0",
  "scikit-learn>=1.5"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3",
  "pytest-asyncio>=0.23",
  "pytest-cov>=5.0",
  "ruff>=0.5",
  "mypy>=1.11"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
pythonpath = ["src"]
asyncio_mode = "auto"
```

**Step 4: Run test to verify pass**

Run: `cd /home/alexandre/projetos/deriv-organismo && pytest tests/unit/test_project_boot.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
cd /home/alexandre/projetos/deriv-organismo
git init
git add .
git commit -m "chore: bootstrap deriv organismo project"
```

---

## Task 2: Adicionar configuração central e `.env.example`

**Objective:** Centralizar configuração e declarar variáveis necessárias sem expor segredos.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/config.py`
- Create: `/home/alexandre/projetos/deriv-organismo/.env.example`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_config.py`

**Step 1: Write failing test**

```python
from deriv_organismo.config import Settings


def test_settings_defaults_support_single_operator_and_future_multitenancy():
    settings = Settings(
        database_url="postgresql+asyncpg://localhost/test",
        redis_url="redis://localhost:6379/0",
    )
    assert settings.default_account_slug == "primary"
    assert settings.enable_multi_tenant is False
```

**Step 2: Run test to verify failure**

Run: `cd /home/alexandre/projetos/deriv-organismo && pytest tests/unit/test_config.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str
    redis_url: str
    deriv_app_id: str = ""
    deriv_api_base_ws: str = "wss://ws.derivws.com/websockets/v3"
    deriv_api_base_rest: str = "https://api.deriv.com"
    default_account_slug: str = "primary"
    enable_multi_tenant: bool = False
```

Use this `.env.example` baseline:

```dotenv
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/deriv_organismo
REDIS_URL=redis://localhost:6379/0
DERIV_APP_ID=
DERIV_API_BASE_WS=wss://ws.derivws.com/websockets/v3
DERIV_API_BASE_REST=https://api.deriv.com
DEFAULT_ACCOUNT_SLUG=primary
ENABLE_MULTI_TENANT=false
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_config.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add .env.example src/deriv_organismo/config.py tests/unit/test_config.py
git commit -m "feat: add central settings module"
```

---

## Task 3: Subir infraestrutura local com Postgres e Redis

**Objective:** Criar ambiente local mínimo para persistência e filas/cache.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/docker-compose.yml`
- Create: `/home/alexandre/projetos/deriv-organismo/Dockerfile`
- Create: `/home/alexandre/projetos/deriv-organismo/Makefile`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_infra_files.py`

**Step 1: Write failing test**

```python
from pathlib import Path


def test_docker_compose_declares_postgres_and_redis():
    content = Path("docker-compose.yml").read_text()
    assert "postgres:" in content
    assert "redis:" in content
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_infra_files.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Use this `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: deriv_organismo
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

Use this `Makefile`:

```make
up:
	docker compose up -d

down:
	docker compose down

test:
	pytest
```

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_infra_files.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add docker-compose.yml Dockerfile Makefile tests/integration/test_infra_files.py
git commit -m "chore: add local infra stack"
```

---

## Task 4: Modelar o contexto de conta e tenancy futura

**Objective:** Criar a abstração account-aware que sustentará single-operator agora e multi-conta depois.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/domain/accounts.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_accounts.py`

**Step 1: Write failing test**

```python
from deriv_organismo.domain.accounts import AccountContext


def test_account_context_isolation_fields_are_required():
    account = AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode="demo",
    )
    assert account.account_slug == "primary"
    assert account.mode == "demo"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_accounts.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel
from typing import Literal


class AccountContext(BaseModel):
    account_id: str
    tenant_id: str
    account_slug: str
    mode: Literal["demo", "real"]
    deriv_login_id: str | None = None
```

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_accounts.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/domain/accounts.py tests/unit/test_accounts.py
git commit -m "feat: add account context abstraction"
```

---

## Task 5: Criar schema inicial do banco com isolamento por conta

**Objective:** Persistir contas, eventos, trades e especialistas com `account_id` obrigatório.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/db/base.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/db/models.py`
- Create: `/home/alexandre/projetos/deriv-organismo/alembic.ini`
- Create: `/home/alexandre/projetos/deriv-organismo/alembic/env.py`
- Create: `/home/alexandre/projetos/deriv-organismo/alembic/versions/20260615_000001_initial_schema.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_models.py`

**Step 1: Write failing test**

```python
from deriv_organismo.db.models import TradeDecision


def test_trade_decision_model_has_account_id():
    columns = TradeDecision.__table__.columns.keys()
    assert "account_id" in columns
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_models.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Minimum SQLAlchemy models to create now:
- `Account`
- `MarketCandle`
- `Specialist`
- `SpecialistVariant`
- `TradeDecision`
- `RiskEvent`
- `LearningEvent`

Each business table must include:

```python
account_id = mapped_column(String, nullable=False, index=True)
```

`TradeDecision` minimum fields:
- `id`
- `account_id`
- `symbol`
- `timeframe`
- `specialist_key`
- `variant_key`
- `regime`
- `decision`
- `confidence`
- `risk_status`
- `created_at`

**Step 4: Run test to verify pass**

Run:
- `pytest tests/unit/test_models.py -v`
- `alembic upgrade head`
Expected: PASS and migration applies cleanly.

**Step 5: Commit**

```bash
git add alembic.ini alembic src/deriv_organismo/db tests/unit/test_models.py
git commit -m "feat: add initial account-aware schema"
```

---

## Task 6: Implementar cliente Deriv de leitura com heartbeat

**Objective:** Conectar com a Deriv para market data e endpoints de sistema sem ainda executar ordens.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/integrations/deriv/client.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/integrations/deriv/messages.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_deriv_client.py`

**Step 1: Write failing test**

```python
from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.integrations.deriv.client import DerivClient


def test_deriv_client_builds_account_aware_request_payload():
    account = AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode="demo",
    )
    client = DerivClient(app_id="1234")
    payload = client.build_ticks_history_request(account=account, symbol="R_100", count=10)
    assert payload["ticks_history"] == "R_100"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_deriv_client.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Create helper methods for:
- `build_ping_request()`
- `build_time_request()`
- `build_active_symbols_request(product_type="basic")`
- `build_ticks_history_request(account, symbol, count, style="candles", granularity=300)`

Client requirements:
- maintain WebSocket connection
- send periodic ping
- reconnect on disconnect
- log request/response metadata without secrets

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_deriv_client.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/integrations/deriv tests/unit/test_deriv_client.py
git commit -m "feat: add deriv read client"
```

---

## Task 7: Implementar catálogo inicial de símbolos synthetic

**Objective:** Congelar a primeira cesta operável de 3 a 5 símbolos com metadados explícitos.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/domain/symbols.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_symbols.py`

**Step 1: Write failing test**

```python
from deriv_organismo.domain.symbols import V1_SYMBOLS


def test_v1_symbols_count_stays_between_three_and_five():
    assert 3 <= len(V1_SYMBOLS) <= 5
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_symbols.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Define `V1_SYMBOLS` with 4 initial candidates, for example:
- `R_50`
- `R_75`
- `R_100`
- `RDBULL`

Each symbol config should include:
- `symbol`
- `label`
- `enabled`
- `timeframes=["1m", "5m", "15m"]`
- `market_type="synthetic"`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_symbols.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/domain/symbols.py tests/unit/test_symbols.py
git commit -m "feat: define v1 synthetic symbols"
```

---

## Task 8: Construir agregador de candles multi-timeframe

**Objective:** Transformar ticks/histórico em candles 1m/5m/15m consistentes.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/candles.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_candles.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.candles import CandleAggregator


def test_candle_aggregator_rolls_one_minute_candles_into_five_minute_bar():
    aggregator = CandleAggregator()
    candles = [
        {"open": 100, "high": 101, "low": 99, "close": 100.5},
        {"open": 100.5, "high": 102, "low": 100, "close": 101},
        {"open": 101, "high": 103, "low": 100.8, "close": 102},
        {"open": 102, "high": 102.5, "low": 101.2, "close": 101.8},
        {"open": 101.8, "high": 104, "low": 101.5, "close": 103},
    ]
    bar = aggregator.rollup(candles)
    assert bar["open"] == 100
    assert bar["close"] == 103
    assert bar["high"] == 104
    assert bar["low"] == 99
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_candles.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Create `CandleAggregator.rollup()` and `CandleFrameStore` that stores bars per:
- `account_id`
- `symbol`
- `timeframe`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_candles.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/candles.py tests/unit/test_candles.py
git commit -m "feat: add candle aggregation service"
```

---

## Task 9: Implementar detector de regime V1

**Objective:** Classificar tendência, range, volatilidade alta e ruído alto de forma auditável.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/domain/regime.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/regime_detector.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_regime_detector.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.regime_detector import RegimeDetector


def test_regime_detector_returns_trend_or_range_labels():
    detector = RegimeDetector()
    regime = detector.classify(
        closes=[100, 101, 102, 103, 104, 105],
        atr_values=[1.0, 1.1, 1.2, 1.2, 1.3, 1.4],
    )
    assert regime.label in {"trend", "range", "high_vol", "high_noise", "no_trade"}
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_regime_detector.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement:
- `RegimeSnapshot`
- trend score from slope / directional consistency
- volatility score from ATR percentile or rolling range
- noise score from wickiness or directional churn

Start simple and deterministic. Do not use ML here yet.

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_regime_detector.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/domain/regime.py src/deriv_organismo/services/regime_detector.py tests/unit/test_regime_detector.py
git commit -m "feat: add initial regime detector"
```

---

## Task 10: Criar contrato base dos especialistas

**Objective:** Definir a interface comum de todos os especialistas técnicos.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/domain/signals.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/specialists/base.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_specialist_contract.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.specialists.base import SpecialistSignal


def test_specialist_signal_contains_risk_relevant_fields():
    signal = SpecialistSignal(
        specialist_key="trend_follow",
        symbol="R_100",
        timeframe="5m",
        direction="long",
        confidence=0.7,
        should_trade=True,
    )
    assert signal.should_trade is True
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_specialist_contract.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Define models for:
- `SpecialistInput`
- `SpecialistSignal`
- `SpecialistDecisionReason`
- `BaseSpecialist.evaluate()`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_specialist_contract.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/domain/signals.py src/deriv_organismo/services/specialists/base.py tests/unit/test_specialist_contract.py
git commit -m "feat: add specialist interface"
```

---

## Task 11: Implementar especialista trend following

**Objective:** Criar o primeiro especialista interpretável para mercado em tendência.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/specialists/trend_follow.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_trend_follow_specialist.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.specialists.trend_follow import TrendFollowSpecialist
from deriv_organismo.domain.signals import SpecialistInput


def test_trend_follow_specialist_trades_when_fast_ma_is_above_slow_ma():
    specialist = TrendFollowSpecialist()
    payload = SpecialistInput(
        symbol="R_100",
        timeframe="5m",
        closes=[100, 101, 102, 103, 104, 105, 106],
        regime_label="trend",
    )
    signal = specialist.evaluate(payload)
    assert signal.specialist_key == "trend_follow"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_trend_follow_specialist.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement a simple MA alignment specialist with configurable parameters:
- `fast_window`
- `slow_window`
- `min_trend_strength`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_trend_follow_specialist.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/specialists/trend_follow.py tests/unit/test_trend_follow_specialist.py
git commit -m "feat: add trend following specialist"
```

---

## Task 12: Implementar especialista mean reversion

**Objective:** Criar o segundo especialista interpretável para mercado em range.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/specialists/mean_reversion.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_mean_reversion_specialist.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.specialists.mean_reversion import MeanReversionSpecialist
from deriv_organismo.domain.signals import SpecialistInput


def test_mean_reversion_specialist_requires_range_regime():
    specialist = MeanReversionSpecialist()
    payload = SpecialistInput(
        symbol="R_75",
        timeframe="5m",
        closes=[100, 99.8, 100.1, 99.9, 100.0, 99.7, 99.6],
        regime_label="range",
    )
    signal = specialist.evaluate(payload)
    assert signal.specialist_key == "mean_reversion"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_mean_reversion_specialist.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement a z-score or Bollinger-style range reversion specialist with configurable thresholds.

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_mean_reversion_specialist.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/specialists/mean_reversion.py tests/unit/test_mean_reversion_specialist.py
git commit -m "feat: add mean reversion specialist"
```

---

## Task 13: Implementar especialista breakout e especialista no-trade

**Objective:** Completar a primeira biblioteca mínima de especialistas V1.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/specialists/breakout.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/specialists/no_trade.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_breakout_specialist.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_no_trade_specialist.py`

**Step 1: Write failing tests**

Create tests asserting:
- breakout specialist only triggers on expansion/confirmation
- no-trade specialist returns `should_trade=False` under `high_noise` and `no_trade`

**Step 2: Run tests to verify failure**

Run:
- `pytest tests/unit/test_breakout_specialist.py -v`
- `pytest tests/unit/test_no_trade_specialist.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement:
- breakout based on recent high/low expansion
- no-trade veto specialist with explicit reason codes

**Step 4: Run tests to verify pass**

Run the same two commands.
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/specialists tests/unit/test_breakout_specialist.py tests/unit/test_no_trade_specialist.py
git commit -m "feat: add breakout and no-trade specialists"
```

---

## Task 14: Criar o meta-agente de seleção e peso

**Objective:** Escolher especialistas ativos por regime e símbolo com regras iniciais transparentes.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/meta_agent.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_meta_agent.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.meta_agent import MetaAgent


def test_meta_agent_prefers_trend_specialist_in_trend_regime():
    agent = MetaAgent()
    selected = agent.select_specialists(regime_label="trend", symbol="R_100")
    assert "trend_follow" in [item.specialist_key for item in selected]
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_meta_agent.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The first version should:
- map regimes to preferred specialists
- apply basic weights
- support pause/reactivate flags
- remain deterministic before ML scoring exists

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_meta_agent.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/meta_agent.py tests/unit/test_meta_agent.py
git commit -m "feat: add initial meta agent"
```

---

## Task 15: Implementar o risco soberano

**Objective:** Vetar operações por regras absolutas antes da execução.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/risk_engine.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/domain/risk.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_risk_engine.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.risk_engine import RiskEngine
from deriv_organismo.domain.risk import RiskInput


def test_risk_engine_blocks_trade_when_account_hits_daily_loss_limit():
    engine = RiskEngine()
    result = engine.evaluate(
        RiskInput(
            account_id="acc_primary",
            symbol="R_100",
            daily_pnl=-101,
            daily_loss_limit=-100,
            recent_loss_streak=1,
            regime_label="trend",
            signal_confidence=0.8,
        )
    )
    assert result.allowed is False
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_risk_engine.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement checks for:
- max risk per trade
- daily loss limit
- recent loss streak
- noisy/no-trade regime
- cooldown active
- specialist paused
- variant quarantine

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_risk_engine.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/risk_engine.py src/deriv_organismo/domain/risk.py tests/unit/test_risk_engine.py
git commit -m "feat: add sovereign risk engine"
```

---

## Task 16: Adicionar score contextual e memória curta/longa

**Objective:** Introduzir o primeiro nível de aprendizado V1 sem delegar a entrada ao ML.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/context_scorer.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/memory.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_context_scorer.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.context_scorer import ContextScorer


def test_context_scorer_weights_recent_and_long_term_performance():
    scorer = ContextScorer()
    score = scorer.score(
        recent_win_rate=0.70,
        long_term_win_rate=0.55,
        regime_match_score=0.80,
    )
    assert 0 <= score <= 1
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_context_scorer.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The first scorer can be a transparent weighted formula. Add memory storage keyed by:
- `account_id`
- `symbol`
- `specialist_key`
- `variant_key`
- `regime_label`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_context_scorer.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/context_scorer.py src/deriv_organismo/services/memory.py tests/unit/test_context_scorer.py
git commit -m "feat: add contextual scoring and memory"
```

---

## Task 17: Implementar o pipeline de decisão ponta a ponta em memória

**Objective:** Conectar candles, regime, especialistas, score, risco e decisão final antes de tocar a API de trade.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/decision_pipeline.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_decision_pipeline.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.decision_pipeline import DecisionPipeline


def test_decision_pipeline_returns_blocked_or_approved_trade_decision():
    pipeline = DecisionPipeline()
    result = pipeline.run(symbol="R_100", timeframe="5m")
    assert result.decision in {"approved", "blocked", "observe"}
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_decision_pipeline.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The pipeline should call, in order:
1. load market frame
2. classify regime
3. select specialists
4. evaluate specialists
5. contextual score
6. sovereign risk
7. create decision artifact

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_decision_pipeline.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/decision_pipeline.py tests/integration/test_decision_pipeline.py
git commit -m "feat: add decision pipeline"
```

---

## Task 18: Implementar executor Deriv para conta demo

**Objective:** Enviar propostas e ordens para demo com isolamento por conta e registro de intenção.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/execution.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/integrations/deriv/trading.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_execution_service.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.execution import ExecutionService
from deriv_organismo.domain.accounts import AccountContext


def test_execution_service_requires_account_context_for_trade_submission():
    service = ExecutionService()
    account = AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode="demo",
    )
    payload = service.build_trade_request(account=account, symbol="R_100", amount=10)
    assert payload.account_id == "acc_primary"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_execution_service.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The demo executor should:
- request proposal
- submit buy on approval
- persist trade decision + execution event
- never execute if mode is `real` and the strategy is not promoted

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_execution_service.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/execution.py src/deriv_organismo/integrations/deriv/trading.py tests/unit/test_execution_service.py
git commit -m "feat: add demo execution service"
```

---

## Task 19: Persistir trilha auditável de eventos

**Objective:** Garantir observabilidade mínima de cada decisão crítica.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/observability/events.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/observability/logger.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_events.py`

**Step 1: Write failing test**

```python
from deriv_organismo.observability.events import build_event


def test_event_builder_requires_account_and_event_type():
    event = build_event(account_id="acc_primary", event_type="risk_blocked", payload={})
    assert event["account_id"] == "acc_primary"
    assert event["event_type"] == "risk_blocked"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_events.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Implement event schemas for at least:
- `regime_detected`
- `specialist_selected`
- `signal_generated`
- `risk_blocked`
- `trade_submitted`
- `trade_result`
- `variant_created`
- `promotion_decision`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_events.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/observability tests/unit/test_events.py
git commit -m "feat: add audit event infrastructure"
```

---

## Task 20: Expor API operacional mínima

**Objective:** Criar endpoints locais para health, status, contas, símbolos, decisões e eventos.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/api/routes_health.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/api/routes_accounts.py`
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/api/routes_events.py`
- Modify: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/main.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_api_routes.py`

**Step 1: Write failing test**

```python
from fastapi.testclient import TestClient
from deriv_organismo.main import create_app


def test_status_endpoint_exists():
    client = TestClient(create_app())
    response = client.get("/status")
    assert response.status_code == 200
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_api_routes.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Expose routes:
- `GET /health`
- `GET /status`
- `GET /accounts`
- `GET /symbols`
- `GET /events`
- `GET /decisions/latest`

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_api_routes.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/api src/deriv_organismo/main.py tests/integration/test_api_routes.py
git commit -m "feat: add operational api routes"
```

---

## Task 21: Implementar laboratório de variantes em demo

**Objective:** Permitir ajuste incremental e clonagem rastreável sem contaminar produção.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/lab.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_lab.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.lab import VariantLab


def test_variant_lab_clones_specialist_with_parent_reference():
    lab = VariantLab()
    variant = lab.clone_variant(
        specialist_key="trend_follow",
        parent_variant_key="trend_follow_v1",
    )
    assert variant.parent_variant_key == "trend_follow_v1"
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_lab.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The lab should support:
- incremental parameter adjustment
- variant cloning
- parent/baseline reference
- quarantine flag by default

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_lab.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/lab.py tests/unit/test_lab.py
git commit -m "feat: add demo variant lab"
```

---

## Task 22: Implementar score composto de promoção

**Objective:** Formalizar a régua demo → real de forma objetiva e auditável.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/promotion.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_promotion.py`

**Step 1: Write failing test**

```python
from deriv_organismo.services.promotion import PromotionScorer


def test_promotion_scorer_blocks_candidate_without_sample_size():
    scorer = PromotionScorer()
    result = scorer.evaluate(
        trade_count=8,
        minimum_trade_count=30,
        net_return=0.12,
        drawdown=0.03,
        stability=0.70,
        regime_score=0.75,
    )
    assert result.eligible is False
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_promotion.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Score inputs:
- net return
- drawdown
- stability
- regime performance
- sample size
- recent degradation
- risk rule adherence

Outputs:
- `eligible`
- `score`
- `reasons`
- `requires_human_approval=True`

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_promotion.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/promotion.py tests/unit/test_promotion.py
git commit -m "feat: add promotion scorer"
```

---

## Task 23: Bloquear real para não-promovidos

**Objective:** Garantir tecnicamente que conta real só execute promovidos.

**Files:**
- Modify: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/services/execution.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/unit/test_real_execution_guard.py`

**Step 1: Write failing test**

```python
import pytest

from deriv_organismo.services.execution import ExecutionService, RealExecutionBlocked
from deriv_organismo.domain.accounts import AccountContext


def test_real_account_cannot_execute_unpromoted_variant():
    service = ExecutionService()
    account = AccountContext(
        account_id="acc_real",
        tenant_id="tenant_primary",
        account_slug="primary-real",
        mode="real",
    )
    with pytest.raises(RealExecutionBlocked):
        service.ensure_real_can_execute(is_promoted=False, account=account)
```

**Step 2: Run test to verify failure**

Run: `pytest tests/unit/test_real_execution_guard.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Add a guard clause that raises a domain exception when:
- mode is `real`
- promoted flag is false
- human approval flag is absent when required

**Step 4: Run test to verify pass**

Run: `pytest tests/unit/test_real_execution_guard.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/services/execution.py tests/unit/test_real_execution_guard.py
git commit -m "feat: guard real execution by promotion state"
```

---

## Task 24: Criar worker de observação contínua

**Objective:** Rodar o ciclo do organismo continuamente para demo.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/workers/market_loop.py`
- Create: `/home/alexandre/projetos/deriv-organismo/scripts/run_market_loop.py`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_market_loop.py`

**Step 1: Write failing test**

```python
from deriv_organismo.workers.market_loop import MarketLoop


def test_market_loop_exposes_single_cycle_runner():
    loop = MarketLoop()
    assert hasattr(loop, "run_cycle")
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_market_loop.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

`MarketLoop.run_cycle()` should:
- fetch/update candles
- run decision pipeline
- submit demo trade when approved
- log decision event

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_market_loop.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/workers/market_loop.py scripts/run_market_loop.py tests/integration/test_market_loop.py
git commit -m "feat: add market loop worker"
```

---

## Task 25: Criar dashboard operacional mínimo

**Objective:** Dar visibilidade local para saúde, contas, eventos e decisões recentes.

**Files:**
- Create: `/home/alexandre/projetos/deriv-organismo/src/deriv_organismo/api/routes_dashboard.py`
- Create: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_dashboard_route.py`

**Step 1: Write failing test**

```python
from fastapi.testclient import TestClient
from deriv_organismo.main import create_app


def test_dashboard_route_exists():
    client = TestClient(create_app())
    response = client.get("/dashboard")
    assert response.status_code == 200
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_dashboard_route.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

Return JSON first, HTML later if desired. Include:
- app status
- account list
- last decisions
- last risk blocks
- last promotions

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_dashboard_route.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/deriv_organismo/api/routes_dashboard.py tests/integration/test_dashboard_route.py
git commit -m "feat: add minimal dashboard route"
```

---

## Task 26: Documentar bootstrap, execução local e readiness

**Objective:** Fechar a V1 com instruções práticas de uso, validação e limites conhecidos.

**Files:**
- Modify: `/home/alexandre/projetos/deriv-organismo/README.md`
- Create: `/home/alexandre/projetos/deriv-organismo/docs/runbooks/local-demo.md`
- Create: `/home/alexandre/projetos/deriv-organismo/docs/runbooks/promotion-readiness.md`
- Test: `/home/alexandre/projetos/deriv-organismo/tests/integration/test_docs_presence.py`

**Step 1: Write failing test**

```python
from pathlib import Path


def test_runbooks_exist():
    assert Path("docs/runbooks/local-demo.md").exists()
    assert Path("docs/runbooks/promotion-readiness.md").exists()
```

**Step 2: Run test to verify failure**

Run: `pytest tests/integration/test_docs_presence.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

The runbooks must cover:
- local setup
- `.env` filling rules without secrets in repo
- starting services
- running tests
- demo-only start
- promotion checklist for real
- known gaps of V1

**Step 4: Run test to verify pass**

Run: `pytest tests/integration/test_docs_presence.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add README.md docs/runbooks tests/integration/test_docs_presence.py
git commit -m "docs: add local demo and readiness runbooks"
```

---

## Verificação final

Run in order:

```bash
cd /home/alexandre/projetos/deriv-organismo
ruff check .
mypy src
pytest -q
alembic upgrade head
docker compose up -d
pytest tests/integration -q
```

Expected:
- lint limpo
- tipagem sem erros novos
- testes unitários e de integração verdes
- migração aplicada
- Postgres e Redis saudáveis

## Handoff recomendado

Depois de salvar este plano, a execução ideal é:
1. implementar tarefa por tarefa
2. revisar aderência ao design após cada tarefa
3. revisar qualidade de código após cada tarefa
4. só então avançar

## Observações arquiteturais finais

- A V1 não deve tentar operar múltiplas contas ainda, mas precisa tratar `account_id` como eixo estrutural obrigatório.
- O primeiro ML deve ser transparente: score contextual e ajuste de parâmetros, não policy livre.
- Se o loop ao vivo ficar instável, congelar em replay/backtest curto antes de continuar com execução demo.
- Não introduzir dígitos antes de estabilizar candles.
- Não introduzir UI sofisticada antes de fechar observabilidade mínima e risco soberano.
