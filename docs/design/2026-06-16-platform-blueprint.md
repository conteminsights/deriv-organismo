# Blueprint da Plataforma Deriv Organismo

Data: 2026-06-16
Escopo: transformar o motor atual em plataforma multi-tenant comercial-ready.

## 1. Objetivo

Construir uma plataforma onde cada tenant possa:
- fazer login próprio
- cadastrar várias contas Deriv (demo e real)
- conectar o token de cada conta
- acompanhar operações em tempo real
- ver performance por conta, estratégia e período
- ter isolamento de dados
- operar com governança e trilha auditável

A arquitetura deve funcionar para:
- uso individual do Alexandre agora
- futura comercialização sem reescrever o núcleo

## 2. Modelo de acesso

- multi-tenant desde a base
- cada tenant tem seu login
- o login do Alexandre será master/superadmin
- master consegue ver todos os tenants
- tenant comum vê só o próprio escopo
- no estágio atual, só o tenant master será usado

## 3. Entidades principais

- Tenant
- User
- TenantUser
- DerivAccount
- DerivCredential
- Strategy
- StrategyVariant
- Execution
- Position
- BalanceSnapshot
- PerformanceSnapshot
- AuditEvent
- Approval

## 4. Fluxo de credenciais

1. tenant faz login
2. entra no admin
3. cadastra uma conta Deriv
4. informa login_id, tipo demo/real e token
5. sistema valida token na Deriv
6. sistema salva credential criptografada
7. conta fica ativa ou marcada com erro
8. tenant pode ativar, pausar, revogar ou remover a conta

## 5. Operação em andamento

Operação em andamento é:
- sinal gerado
- ordem enviada
- ordem aberta
- posição viva
- PnL flutuante em tempo real
- saída/fechamento com PnL realizado

Tela operacional precisa mostrar:
- conta
- símbolo
- estratégia/variante
- entrada
- saída
- lucro/prejuízo
- status
- motivo/razão da decisão

## 6. Relatórios de performance

Por:
- conta
- estratégia
- variante
- período
- tenant

Indicadores:
- saldo inicial/final
- ganho
- perda
- win rate
- drawdown
- PnL realizado
- PnL por período

## 7. Telas mínimas

- Login
- Admin de contas
- Operações em andamento
- Histórico de operações
- Performance por conta
- Performance agregada
- Aprovações/governança
- Auditoria/eventos

## 8. Rotas mínimas da plataforma

- /admin/accounts
- /admin/credentials
- /ops/live
- /ops/history
- /reports/performance
- /reports/account
- /governance/approvals
- /audit/events

## 9. Ordem de implementação

Fase 1 — fundação
1. modelo multi-tenant de dados
2. migrações
3. credenciais criptografadas
4. validação de token
5. persistência de contas por tenant

Fase 2 — operação
6. coletor de posições/ordens por conta
7. painel de operações em tempo real
8. fechamento/realização de PnL

Fase 3 — inteligência
9. integração do motor com contas reais do tenant
10. histórico operacional por conta e estratégia
11. relatórios de performance

Fase 4 — governança e UX
12. promoções demo -> real
13. aprovações humanas
14. auditoria
15. polimento visual e dashboards avançados
