# Promotion readiness runbook

## Objetivo

Definir a checagem mínima antes de liberar qualquer variante para conta real.

## Checklist de promoção

Antes de considerar promoção:
- `trade_count` acima do mínimo configurado
- `net_return` positivo e consistente
- `drawdown` controlado
- `stability` aceitável
- `regime_score` aceitável
- aderência às regras de risco
- ausência de degradação recente relevante

## Guardas obrigatórias para real

Conta real só pode executar quando:
- a estratégia/variante estiver promovida
- a conta estiver em `mode=real`
- a aprovação humana existir quando requerida

## Validação prática

1. Rodar testes:
   - `uv run pytest tests -q`
2. Verificar score composto de promoção
3. Confirmar que o guard de execução real bloqueia não-promovidos
4. Revisar eventos e decisões recentes no dashboard/rotas

## Gaps conhecidos da V1

- promoção ainda usa score composto simples
- ainda não há trilha persistente em banco para toda a jornada
- worker contínuo ainda é básico
- falta pipeline operacional completo de aprovação humana persistida
- falta endurecer integração real com Deriv antes de uso produtivo

## Regra final

Se houver dúvida, manter em demo.
