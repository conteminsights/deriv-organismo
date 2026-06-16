# Promotion readiness runbook

## Objetivo

Definir a checagem mínima antes de liberar qualquer estratégia ou variante para conta real.

## Princípio operacional

Se houver dúvida, permanece em demo.
Promoção aqui não é marketing de performance; é liberação controlada de risco.

## Checklist de promoção

Antes de considerar promoção, verificar pelo menos:
- `trade_count` acima do mínimo configurado
- `net_return` positivo e consistente
- `drawdown` controlado
- `stability` aceitável
- `regime_score` aceitável
- aderência às regras de risco
- ausência de degradação recente relevante
- coerência entre comportamento esperado e comportamento observado

## Guardas obrigatórias para real

Conta real só pode executar quando:
- a estratégia ou variante estiver promovida
- a conta estiver em `mode=real`
- a aprovação humana existir quando requerida
- o bloqueio para não-promovidos continuar íntegro

## Validação prática

1. Rodar testes:
   - `uv run pytest tests -q`
2. Rodar tipagem:
   - `uv run mypy src`
3. Revisar score composto de promoção
4. Confirmar que o guard de execução real bloqueia não-promovidos
5. Revisar eventos, decisões e dashboard
6. Confirmar que a operação ainda faz mais sentido em demo do que em real

## O que falta antes de chamar isso de pronto para real

- promoção ainda usa score composto simples
- ainda não há trilha persistente completa para toda a jornada operacional
- worker contínuo ainda é básico
- falta pipeline operacional maduro para aprovação humana persistida
- falta endurecer a integração real com Deriv
- falta interface operacional mais rica para revisão manual rápida

## Critério conservador

Mesmo com score aceitável, não promover se houver:
- comportamento errático recente
- mudança estrutural ainda não observada em amostra suficiente
- lacuna de observabilidade
- dúvida sobre risco soberano
- dependência excessiva de componentes stubados

## Regra final

Se a pergunta for "já dá para pôr em real?", a resposta padrão da V1 deve ser:
- ainda não, sem revisão explícita e evidência suficiente
