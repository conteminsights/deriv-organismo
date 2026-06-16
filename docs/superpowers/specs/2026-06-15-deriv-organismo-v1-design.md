# Organismo Autônomo Deriv — Design da V1

## 1. Resumo executivo

Este documento define a V1 de um organismo autônomo para operar na Deriv via API.

Objetivo central:
- preservar capital em primeiro lugar
- buscar consistência operacional
- aprender de forma adaptativa sem romper as regras de risco

A V1 não será um "modelo mágico" único. Ela será um sistema hierárquico com:
- leitura de mercado por candles
- especialistas interpretáveis por regime
- meta-agente de seleção e peso
- ML para filtro contextual e ajuste de parâmetros
- risco soberano acima de qualquer decisão de entrada
- ambiente demo como laboratório vivo
- conta real recebendo apenas sinais promovidos

Escolhas validadas nesta fase:
- Deriv via API oficial
- operação autônoma
- foco inicial em candles
- synthetic indices como universo inicial
- 3 a 5 símbolos
- multi-timeframe com 5m como timeframe mestre
- conta demo como ambiente principal de aprendizado
- conta real apenas com estratégias/sinais promovidos
- arquitetura-base: meta-agente com especialistas por regime
- entrada gerada por regras técnicas; ML filtra, prioriza, contextualiza e ajusta parâmetros
- desenho preparado desde já para evolução futura para multi-tenant/multi-conta, com múltiplas credenciais de API isoladas por conta

## 2. Objetivo da V1

A V1 existe para provar cinco hipóteses:
1. a integração com a API da Deriv funciona de ponta a ponta
2. o organismo consegue ler contexto de mercado de forma útil
3. especialistas técnicos podem ser geridos por regime com benefício operacional
4. o aprendizado adaptativo melhora seleção e parametrização sem perder governança
5. a camada de risco evita degradação burra e protege capital

A V1 não busca maximizar agressividade. Ela busca validar uma primeira forma viável, governável e evolutiva do organismo.

## 3. Princípios de projeto

1. Capital antes de inteligência
- nenhuma capacidade adaptativa pode violar limites de risco

2. Consistência antes de ambição
- o sistema deve preferir operar menos a operar mal

3. Aprendizado com contenção
- o organismo pode evoluir, mas não pode se remodelar diretamente em produção real

4. Interpretabilidade operacional
- sinais devem nascer de regras compreensíveis
- ML atua como filtro, priorizador e afinador, não como oráculo opaco na V1

5. Separação entre laboratório e produção
- demo aprende, testa, falha e evolui
- real recebe apenas ativos promovidos e monitorados

6. Arquitetura preparada para tenancy futura
- embora a V1 opere um único contexto principal, entidades, credenciais e eventos devem nascer com isolamento por conta/API
- o objetivo é permitir evolução posterior para múltiplas contas e múltiplos tenants sem refatoração estrutural total

7. Auditoria por evento
- promoção, rebaixamento, pausa, veto, cooldown, rollback e execução precisam gerar registro auditável

## 4. Escopo funcional da V1

### Entra na V1
- integração com API da Deriv
- operação em conta demo
- trilha de replicação controlada em conta real
- modelagem interna account-aware para permitir evolução futura para multi-tenant/multi-conta sem refatoração estrutural total
- leitura de candles em synthetic indices
- universo inicial de 3 a 5 símbolos
- leitura multi-timeframe
  - 15m para contexto
  - 5m como decisão mestre
  - 1m para timing fino
- detector de regime
- biblioteca inicial de especialistas interpretáveis
- ML para filtro contextual, score de confiança e ajuste de parâmetros
- memória curta, longa, contextual e de linhagem
- laboratório evolutivo na demo
- score composto de promoção
- comitê híbrido de promoção
- risco soberano
- logs e trilha de auditoria

### Não entra na V1
- dígitos
- universo amplo de símbolos
- autonomia irrestrita em conta real
- operação multi-tenant ativa já na V1
- modelo dominante de caixa-preta
- remodelagem livre em produção
- expansão multi-mercado grande
- abordagem "quântica" ou buzzword sem justificativa operacional

## 5. Arquitetura-base

A arquitetura da V1 será composta por nove blocos.

1. Coletor de mercado
- recebe candles e dados auxiliares dos símbolos monitorados
- organiza a visão multi-timeframe
- alimenta as camadas superiores com dados limpos e consistentes

2. Leitor de contexto e regime
- classifica o mercado em regimes operacionais
- exemplos iniciais:
  - tendência limpa
  - lateralização/range
  - expansão de volatilidade
  - ruído alto
  - condição imprópria para operar

3. Biblioteca de especialistas
- reúne estratégias técnicas interpretáveis
- cada especialista possui regras, parâmetros, limites e histórico próprio
- especialistas são avaliados por símbolo, regime e timeframe

4. Meta-agente de seleção e peso
- decide quais especialistas ficam ativos em cada contexto
- ajusta pesos relativos e confiança operacional
- ajusta parâmetros dentro de faixas pré-definidas
- pode pausar ou reativar especialistas conforme desempenho

5. Camada soberana de risco
- autoridade máxima do organismo
- valida risco por trade, condição operacional e elegibilidade de execução
- pode vetar qualquer sinal, mesmo quando o especialista e o meta-agente querem operar

6. Executor Deriv
- converte decisão aprovada em chamadas da API da Deriv
- registra intenção, contexto, variante, parâmetros e resposta da corretora
- já deve operar sobre uma abstração de conta/credencial, mesmo que a V1 use inicialmente um único operador principal

7. Memória operacional
- preserva histórico curto, longo, contextual e genealógico dos especialistas
- sustenta seleção adaptativa e comparação entre baseline e variantes

8. Laboratório evolutivo em demo
- local de ajuste incremental, clonagem de variantes, competição controlada e coleta de evidência
- nenhuma variante nova sobe direto ao real

9. Comitê de promoção para real
- combina score composto, leitura do meta-agente e supervisão humana inicial
- decide promoção, rebaixamento, quarentena ou rollback

## 6. Fluxo operacional

O organismo seguirá o ciclo abaixo.

1. Observação
- o coletor recebe candles dos synthetic indices definidos
- consolida a leitura multi-timeframe

2. Interpretação
- o leitor de regime classifica o contexto atual
- produz um estado operacional utilizável pelo meta-agente

3. Seleção
- o meta-agente consulta histórico por regime, símbolo e horizonte
- escolhe quais especialistas podem falar
- ajusta pesos e parâmetros permitidos

4. Geração de sinais
- cada especialista emite ou não um sinal técnico
- os sinais nascem de regras técnicas interpretáveis
- ML filtra, pontua contexto, ordena prioridade e corta sinais ruins

5. Veto soberano
- risco valida elegibilidade do trade
- se qualquer trava crítica estiver ativa, o sinal é bloqueado

6. Execução
- o executor envia a ordem pela API da Deriv
- toda decisão executada ou vetada é registrada

7. Aprendizado
- após o ciclo operacional, o sistema atualiza métricas recentes e históricas
- reavalia aderência por regime, confiança e necessidade de pausa ou ajuste

8. Evolução
- no ambiente demo, especialistas podem ser ajustados ou clonados em variantes
- variantes competem com baselines em condições comparáveis
- somente variantes aprovadas podem ser elegíveis para real

## 7. Universo operacional inicial

### Mercado
- Deriv
- synthetic indices

### Modalidade
- candles

### Símbolos
- 3 a 5 símbolos na V1
- a seleção exata será definida no planejamento de implementação
- deve-se preferir um conjunto pequeno, com boa disponibilidade operacional e diversidade suficiente de comportamento

### Timeframes
- 15m = contexto macro operacional
- 5m = timeframe mestre de decisão
- 1m = timing fino de entrada

## 8. Especialistas iniciais

A biblioteca inicial deverá nascer de estratégias clássicas e interpretáveis, com uma camada de ML por cima.

Famílias candidatas:
- trend following
- mean reversion
- breakout
- expansão/contração de volatilidade
- especialista de "não operar" em ruído alto

Regras da camada de especialistas:
- o sinal principal nasce de regras técnicas
- cada especialista possui parâmetros ajustáveis, porém limitados
- ajustes devem ocorrer dentro de faixas previamente definidas
- nenhum especialista pode redefinir sozinho regras soberanas de risco

## 9. Papel do ML na V1

Na V1, o aprendizado de máquina tem quatro papéis centrais:

1. Filtro contextual
- reconhecer quando um sinal técnico faz sentido no contexto atual

2. Score de confiança
- pontuar a qualidade esperada do sinal com base em regime, símbolo, timeframe e desempenho histórico

3. Ajuste de parâmetros
- adaptar sensibilidade, filtros e gatilhos dentro de limites seguros

4. Governança adaptativa de especialistas
- ajudar a escolher, pesar, pausar, reativar e comparar especialistas por contexto

O ML não terá autonomia para:
- inventar livremente novas entradas diretamente em produção real
- furar limites de risco
- promover variantes ao real sem passar pelo comitê definido

## 10. Modelo de aprendizado e evolução

A V1 aprende em três níveis.

### 10.1 Aprendizado de seleção
O meta-agente aprende:
- quais especialistas performam melhor por regime
- em quais símbolos cada especialista tem mais aderência
- quando reduzir prioridade ou pausar um especialista

### 10.2 Aprendizado de parametrização
Cada especialista pode ajustar, entre outros:
- sensibilidade de entrada
- filtros de volatilidade
- distância de confirmação
- timing de gatilho

Todos os ajustes devem respeitar faixas pré-aprovadas.

### 10.3 Aprendizado evolutivo controlado
Quando um especialista piora ou há hipótese realista de melhoria, o organismo pode:
- aplicar ajuste incremental
- clonar uma variante próxima
- rodar testes comparativos em demo
- decidir manter baseline, promover variante, rebaixar ou descartar

Princípio-chave:
- remodelagem existe, mas em quarentena experimental
- não existe remodelagem livre diretamente no real

## 11. Memória operacional

A memória do organismo será híbrida.

1. Memória curta
- privilegia comportamento recente
- responde a mudanças de regime e degradação rápida

2. Memória longa
- preserva aprendizado validado ao longo do tempo
- evita amnésia operacional por janelas curtas de sorte ou azar

3. Memória contextual
- registra em quais regimes, símbolos e condições cada especialista foi bem ou mal

4. Memória de linhagem
- registra de quem cada variante nasceu
- quais mudanças foram feitas
- por que houve promoção, rebaixamento, pausa ou descarte

Conteúdo mínimo por especialista/variante:
- performance
- contexto de acerto e falha
- parâmetros ativos
- pai/baseline de origem
- data/condição de promoção ou quarentena

## 12. Risco soberano e proteção operacional

Hierarquia de autoridade:
1. risco soberano
2. restrições operacionais da conta
3. comitê de promoção
4. meta-agente
5. especialistas

Bloqueios principais da V1:
- risco máximo por operação
- limite de perda diária
- perda acumulada por janela
- sequência ruim recente
- regime inadequado ou ruído alto
- degradação recente de performance
- cooldown automático
- trava por símbolo
- trava por especialista
- trava por variante recém-promovida

Comportamento esperado:
- o organismo pode passar horas sem operar
- ausência de trade aceitável é comportamento saudável
- confiança baixa implica observação, não execução forçada

## 13. Governança de ambientes

### Demo
- principal laboratório de aprendizado
- lugar de testes, competição e remodelagem controlada
- coleta evidência para promoção
- no desenho interno, cada experimento e credencial deve permanecer isolado por conta

### Real
- recebe apenas sinais e especialistas promovidos
- inicia com lote mínimo e postura conservadora inteligente
- humano aprova promoções iniciais
- humano pode vetar estratégias ou variantes
- degradação relevante implica quarentena ou rollback
- a evolução futura para múltiplas contas deve preservar isolamento de risco, memória e auditoria por conta/API

## 14. Comitê híbrido de promoção

A promoção demo → real será decidida por score composto mais leitura contextual.

Componentes esperados do score:
- retorno líquido
- drawdown
- estabilidade
- performance por regime
- tamanho mínimo de amostra
- degradação recente
- aderência às regras de risco

Estrutura decisória:
- regras objetivas do score composto
- opinião do meta-agente
- supervisão humana na fase inicial do real

Nenhuma variante sobe ao real por entusiasmo estatístico curto.

## 15. Frequência operacional e postura de execução

Postura escolhida:
- conservador inteligente

Faixa operacional inicial desejada:
- frequência adaptativa por regime
- faixa-guia de 1 a 6 operações por símbolo/dia
- sem obrigação de operar

Kill-switch operacional:
- parar por limite de perda
- parar por regime ruim ou ruído alto
- parar por queda recente de performance
- aplicar janela automática de resfriamento

## 16. Observabilidade e trilha auditável

Toda decisão relevante deve gerar evento rastreável.

Eventos mínimos:
- leitura de regime
- ativação/pausa de especialista
- ajuste de parâmetros
- geração de sinal
- veto de risco
- execução enviada
- resposta da API
- promoção/rebaixamento/quarentena
- criação de variante
- rollback
- acionamento de cooldown

Objetivo:
- permitir auditoria humana
- facilitar debug
- comparar causa e efeito de adaptações
- evitar autoengano analítico

## 17. Critérios de sucesso da V1

A V1 será considerada bem-sucedida se provar, com evidência operacional, que:
- integra com a Deriv sem fragilidade estrutural
- executa o ciclo observação → interpretação → seleção → veto → execução → aprendizado
- mantém risco soberano funcionando de verdade
- melhora seleção e parametrização por contexto ao longo do tempo
- separa laboratório demo e produção real com disciplina
- permite supervisão humana efetiva no início

## 18. Riscos principais e contenções

1. Overfitting
- contenção: amostra mínima, score composto, comparação contra baseline, promoção lenta

2. Complexidade excessiva cedo
- contenção: limitar V1 a candles, synthetic, 3 a 5 símbolos e especialistas interpretáveis

3. Caixas-pretas sedutoras demais
- contenção: ML como filtro/contexto e não como árbitro absoluto da entrada

4. Mutação em produção
- contenção: remodelagem apenas em demo/sandbox com promoção controlada

5. Execução burra em mercado ruim
- contenção: detector de regime, veto soberano, cooldown e postura sem obrigação de operar

## 19. Próximos passos de planejamento

Após aprovação deste design, o próximo documento deve detalhar a implementação em etapas.

Esse plano deve cobrir ao menos:
- arquitetura de serviços/módulos
- modelo de dados e eventos
- integração concreta com endpoints da Deriv
- seleção inicial dos símbolos
- desenho do detector de regime
- catálogo inicial de especialistas
- estrutura do score composto
- política de promoção/quarentena/rollback
- observabilidade e dashboards mínimos
- critérios de readiness para demo e para real

## 20. Decisão arquitetural recomendada

A recomendação consolidada para a V1 é:
- usar a abordagem híbrida adaptativa
- com disciplina operacional conservadora
- e espaço futuro para laboratório mais ambicioso depois da estabilização

Em uma frase:
- organismo vivo, sim; caótico, não.