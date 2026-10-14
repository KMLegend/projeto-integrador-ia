# Briefing complementar — Entregável 03

Projeto Integrador IV · Gestão de TI com Ênfase em IA
Prova de Conceito — Machine Learning Clássico · Gestão Preditiva de Estoque com IA
Entrega: 16/09/2026

Fundamentação teórica e de contexto para sustentar a apresentação oral da Entrega 03 — o "porquê" por trás de cada decisão do notebook `entregavel_02_e_03_resumido.ipynb`.

Versão com design publicada como Artifact: https://claude.ai/code/artifact/8b47c012-0a6b-4fc1-8e03-3bdfcf577109

---

## Onde isso se encaixa

Percurso do semestre (conforme `ROTEIRO_PI_IV.docx`):

`01 Problema (feito) → 02 Dataset (feito) → 03 ML Clássico (atual) → 04 Otimização evolutiva → 05 Integração → ... → 09 Apresentação final (16/12)`

> \* Etapa 04 (23/09) segue pendente de confirmação com os professores de Computação Evolutiva quanto ao nível da turma — pode ser reposicionada, segundo o roteiro.

Nos períodos 1 a 3 do curso, a entrega era criar uma ideia, modelar, documentar e trazer telas. A partir do PI IV o eixo muda: o grupo já sabe modelar, documentar e implementar — então o foco passa a ser **aplicar Inteligência Artificial sobre um dado real**, com documentação mínima e implementação máxima. É por isso que o roteiro pede, para a Etapa 03, apenas um notebook rodando sem erros e comentado — nenhum documento à parte é exigido.

A Entrega 03 é a primeira vez que o grupo mexe com um modelo de fato treinado (a Entrega 02 cuidou só da modelagem do dado). Ela se apoia em três frentes vistas em paralelo neste período:

- **Introdução à IA** — fluxo prático fit / predict / métrica
- **Matemática para IA** — mínimos quadrados e sistemas lineares
- **Computação Evolutiva** — vai reaproveitar este mesmo modelo na Etapa 04

Vale abrir a apresentação citando essa mudança de eixo: mostra que o grupo entende *por que* a entrega é um notebook enxuto, e por que a regressão linear (não um modelo mais sofisticado) é a escolha certa neste estágio.

---

## Fundamentação técnica

### 1. Por que regressão, e não classificação — *técnico*
A variável-alvo `demanda_futura` é uma quantidade contínua, não uma categoria. Por isso o problema é de **regressão** supervisionada — se a pergunta fosse "esse produto vai faltar sim/não", seria classificação. A escolha do tipo de modelo nasce da pergunta de negócio, não de preferência técnica.

### 2. A matemática por trás da regressão linear — *técnico*
O modelo aprende um coeficiente para cada uma das 5 features e um intercepto, buscando a combinação linear que minimiza o erro quadrático entre previsão e valor real — o método dos **mínimos quadrados**, mesmo conteúdo de sistemas lineares visto em Matemática para IA, aqui aplicado a dado real. `modelo.fit(X_treino, y_treino)` resolve esse sistema de otimização; `modelo.predict(X_teste)` aplica os coeficientes já aprendidos a dados novos. Os pesos podem ser inspecionados com `modelo.coef_` — útil se a banca perguntar qual feature pesa mais.

### 3. Features não nascem do modelo, nascem da decisão — *negócio*
As 5 features usadas (`estoque_atual`, `saidas_7_dias`, `saidas_30_dias`, `preco`, `promocao`) são exatamente as justificadas na Entrega 02. O modelo não "descobre" sozinho o que é relevante — ele aprende pesos em cima do que o grupo já definiu como relevante para o problema de reposição de estoque. Separar isso com clareza na fala evita a pergunta "por que essas features e não outras": a resposta é a continuidade com a Entrega 02, não o algoritmo.

### 4. Por que separar treino e teste — *técnico*
Se o modelo fosse avaliado nos mesmos dados usados para aprender, pareceria bom mesmo tendo apenas memorizado ruído (**overfitting**). Reservar 20% dos registros que o modelo nunca viu simula o cenário real: prever a demanda de uma semana que ainda não aconteceu.

- 120 registros simulados no total
- Split 80/20 → **96 treino / 24 teste**
- Seed fixa, para a demonstração ser reproduzível ao vivo

### 5. MAE: o que a métrica realmente diz — *técnico*
**MAE = 4,76** significa que, em média, a previsão erra por ~5 unidades de produto — na mesma escala do problema, fácil de comunicar a um gestor de estoque. Diferente do MSE, que eleva o erro ao quadrado e perde a escala original. O MAE também trata todo erro igual, sem punir mais forte previsões muito erradas (diferente do RMSE) — escolha adequada para uma prova de conceito.

Nos 10 primeiros casos de teste (real vs. previsto), os pontos ficam próximos da diagonal ideal (real = previsto), coerente com o MAE de 4,76 — nenhum erro grande isolado puxando a média.

### 6. Da previsão à decisão — *negócio*
A regra "estoque abaixo da previsão → possível falta; estoque acima de 1,8× a previsão → possível excesso" fecha o ciclo: transforma um número estatístico numa recomendação que um gestor de estoque entende sem saber o que é regressão. Essa é a "última milha" que a prova de conceito precisa mostrar — e também a ponte direta para a Entrega 04, que reaproveita este mesmo modelo treinado para decidir quanto comprar de cada produto dentro de um orçamento limitado.

---

## Perguntas prováveis da banca

**Por que regressão linear, e não um modelo mais sofisticado (árvore, rede neural)?**
O objetivo desta etapa é provar o fluxo fim a fim com um modelo simples e interpretável — o roteiro pede explicitamente "prova de conceito", mesma lógica prática usada em Introdução à IA. A regressão linear expõe coeficientes fáceis de explicar oralmente; modelos mais complexos exigiriam mais dado e mais tempo de ajuste, fora do escopo desta entrega.

**O dataset é simulado — isso invalida o modelo?**
Não para os fins desta etapa: o roteiro permite dado real, público ou simulado já na Entrega 02, e a prova de conceito da Entrega 03 herda essa mesma base. O valor está em provar o fluxo completo (dataset → features → treino → métrica → decisão), que se mantém igual quando o dataset real da empresa entrar.

**Por que 80/20 na divisão treino/teste, e não outra proporção?**
Convenção comum quando o dataset é pequeno (120 registros): garante um teste com tamanho relevante (24 registros) sem sacrificar demais o treino. Não é uma regra fixa — mais dado de treino tende a melhorar o ajuste, mas é preciso sobrar teste suficiente para a métrica ser confiável.

**Um MAE de 4,76 é bom?**
Depende da escala do produto: para um item que vende de 30 a 100 unidades por semana, um erro médio de ~5 é relativamente pequeno — bom sinal para uma prova de conceito. Para um item de baixo giro, o mesmo erro absoluto pesa proporcionalmente mais. Vale comparar o MAE com a média da variável-alvo na apresentação para dar essa noção de proporção.

**Isso já está pronto para uso em produção?**
Não — é uma prova de conceito com dado simulado, seed fixa para reprodutibilidade e dataset pequeno. Falta validar com dado real da empresa, um volume maior de histórico e, provavelmente, comparação com outros modelos antes de qualquer decisão real de compra.

**Como isso conecta com a próxima entrega (Computação Evolutiva)?**
O modelo treinado aqui é reaproveitado sem retreinar na Etapa 04: a previsão de demanda vira a "necessidade de reposição" que o algoritmo genético tenta atender dentro de um orçamento limitado. A Entrega 03 fornece o dado de entrada — quanto cada produto vai precisar; a Entrega 04 decide como gastar o orçamento para atender essa necessidade.

---

## Glossário rápido

- **Feature** — coluna do dataset usada como entrada do modelo; decisão de negócio, não do algoritmo.
- **Variável-alvo** — o que o modelo tenta prever; aqui, `demanda_futura`, uma quantidade contínua.
- **Overfitting** — quando o modelo memoriza os dados de treino em vez de aprender o padrão geral.
- **fit / predict** — aprender os coeficientes a partir do treino, depois aplicá-los a dados novos.
- **MAE** — erro médio absoluto: média da diferença, sem sinal, entre previsão e valor real.
- **Split treino/teste** — separar dados de aprendizado dos dados de avaliação, para medir generalização.

---

## Gancho para a Entrega 04

Fechar a apresentação da Entrega 03 lembrando que o `modelo` treinado aqui não é descartado — ele é o ponto de partida da Etapa 04 (Computação Evolutiva), que usa a demanda prevista para decidir, dentro de um orçamento fixo, quanto comprar de cada produto. Mostrar essa continuidade reforça que o projeto tem um fio condutor único: dado → previsão → decisão, e não cinco entregas soltas.
