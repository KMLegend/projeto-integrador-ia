# Guia de Estudo — Regressão Linear

Aprofundamento dos conceitos técnicos da Entrega 03, com cálculos manuais a partir dos dados reais de `entregavel_02_e_03_resumido.ipynb`.

Versão com design publicada como Artifact: https://claude.ai/code/artifact/e483c8fe-c019-45eb-b077-af89f5bb41c5

---

## 1. Aprendizado supervisionado, em uma frase

Dado um conjunto de exemplos onde já se conhece a resposta certa — no projeto, os registros históricos de estoque com a demanda que de fato ocorreu — o objetivo é aprender uma função que aproxime essa resposta bem o suficiente para prever casos novos, ainda não observados. Formalmente: dado `(X, y)`, aprender `f(X) ≈ y` que generalize.

Duas famílias cobrem a maioria dos problemas desse tipo:

- **Regressão** — `y` é uma quantidade contínua (quantas unidades serão vendidas). É o caso do projeto: `demanda_futura` é um número, não uma etiqueta.
- **Classificação** — `y` é uma categoria (o produto vai faltar: sim ou não). Não é o caso desta entrega, mas útil saber nomear a diferença.

Existe uma terceira família, o aprendizado *não supervisionado* (agrupar dados sem saber a resposta certa de antemão) — fora do escopo aqui, mas vale reconhecer o nome.

---

## 2. Regressão linear por dentro

### A forma do modelo

```
ŷ = w0 + w1·x1 + w2·x2 + … + wn·xn
```

No notebook:

```
demanda_prevista = w0 + w1·estoque_atual + w2·saidas_7_dias + w3·saidas_30_dias + w4·preco + w5·promocao
```

Cada `w` é um número que o treino descobre; cada `x` é o valor daquela feature em um registro específico. Os pesos podem ser vistos com `modelo.coef_` e o intercepto com `modelo.intercept_`.

### O que "aprender" significa

Treinar é escolher os `w` que tornam a soma dos erros ao quadrado, entre a previsão e o valor real, a menor possível no conjunto de treino — o **método dos mínimos quadrados**. Geometricamente: entre infinitas retas (ou hiperplanos, com várias features) possíveis, o algoritmo escolhe a que passa mais perto, na vertical, de todos os pontos observados ao mesmo tempo.

### Exemplo resolvido (1 feature, para ver o mecanismo)

4 pares (x, y): (1,2), (2,3), (3,5), (4,4)

| x | y | x − x̄ | y − ȳ | (x−x̄)(y−ȳ) | (x−x̄)² |
|---|---|--------|--------|-------------|---------|
| 1 | 2 | −1.5 | −1.5 | 2.25 | 2.25 |
| 2 | 3 | −0.5 | −0.5 | 0.25 | 0.25 |
| 3 | 5 | 0.5 | 1.5 | 0.75 | 0.25 |
| 4 | 4 | 1.5 | 0.5 | 0.75 | 2.25 |

x̄ = 2.5 · ȳ = 3.5 · Σ(x−x̄)(y−ȳ) = 4.0 · Σ(x−x̄)² = 5.0

```
w1 = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)² = 4.0 / 5.0 = 0.8
w0 = ȳ − w1·x̄ = 3.5 − 0.8×2.5 = 1.5
```

Reta encontrada: `ŷ = 1.5 + 0.8x`. É exatamente esse cálculo que `modelo.fit(X_treino, y_treino)` resolve no notebook — só que com 5 variáveis de uma vez, via álgebra linear com matrizes em vez de somatórios manuais.

---

## 3. Métricas, calculadas à mão com os dados do seu notebook

```
MAE  = (1/n) · Σ |yi − ŷi|
MSE  = (1/n) · Σ (yi − ŷi)²
RMSE = √MSE
R²   = 1 − ( Σ(yi−ŷi)² / Σ(yi−ȳ)² )
```

**MAE** é a distância média, sem sinal, entre real e previsto — na escala original. **MSE** faz o mesmo mas eleva ao quadrado antes de tirar a média, o que pune mais forte erros grandes. **RMSE** é o MSE "trazido de volta" pra escala original (raiz quadrada), por isso é sempre ≥ MAE. **R²** compara o erro do modelo com o erro de um modelo ingênuo que sempre prevê a média — 1 é perfeito, 0 significa "tão bom quanto chutar a média".

### Exemplo resolvido — 10 primeiras linhas de `comparacao`

| real (y) | previsto (ŷ) | erro | \|erro\| | erro² |
|---|---|---|---|---|
| 58 | 50.1 | 7.9 | 7.9 | 62.41 |
| 50 | 37.8 | 12.2 | 12.2 | 148.84 |
| 65 | 69.4 | −4.4 | 4.4 | 19.36 |
| 51 | 46.2 | 4.8 | 4.8 | 23.04 |
| 44 | 49.9 | −5.9 | 5.9 | 34.81 |
| 124 | 118.0 | 6.0 | 6.0 | 36.00 |
| 106 | 98.0 | 8.0 | 8.0 | 64.00 |
| 60 | 59.5 | 0.5 | 0.5 | 0.25 |
| 56 | 54.0 | 2.0 | 2.0 | 4.00 |
| 79 | 78.6 | 0.4 | 0.4 | 0.16 |

n = 10 · ȳ = 69.3 · Σ\|erro\| = 52.1 · Σerro² = 392.87

```
MAE  = 52.1 / 10 = 5.21
MSE  = 392.87 / 10 = 39.29
RMSE = √39.29 ≈ 6.27
```

RMSE (6.27) > MAE (5.21) nessa amostra — exatamente porque o erro de 12.2 (linha 2) pesa mais ao ser elevado ao quadrado.

Com Σ(y−ȳ)² = 6190.10 (soma dos desvios de y em relação à sua própria média):

```
R² = 1 − 392.87/6190.10 ≈ 0.94
```

O modelo explica cerca de 94% da variação da demanda nessa amostra.

> **Por que o número bate diferente do notebook?** O notebook reporta MAE = 4.76, calculado sobre os 24 registros de teste. Aqui, calculando à mão só com os 10 primeiros, o MAE deu 5.21. Isso não é erro de conta: é **variância amostral** — uma métrica calculada sobre poucos pontos é mais sensível a um único erro grande (como o 12.2 da linha 2). Quanto maior o conjunto de teste, mais estável a métrica fica.

---

## 4. Treino, teste e overfitting

Um modelo overfitado "decora" o ruído específico dos dados de treino em vez de aprender o padrão geral — erro baixo no treino, erro alto em dados novos. Um modelo underfitado é simples demais para captar até o padrão óbvio — erro alto nos dois. O conjunto de teste (os 20% que o modelo nunca viu) é o que revela qual dos dois está acontecendo.

A regressão linear, por ser um modelo relativamente rígido (uma soma ponderada, sem curvas complexas), tende a ser menos propensa a overfitting severo do que modelos mais flexíveis — mas isso não substitui a validação no teste, só reduz o risco.

`random_state=42` não deixa o modelo mais preciso — ele só fixa a "moeda" usada para embaralhar os dados antes de dividir, garantindo que a demonstração seja reproduzível.

> **Se quiser ir além:** um único split treino/teste dá uma estimativa da métrica, mas ela varia dependendo de qual 20% caiu no teste. A **validação cruzada (k-fold)** resolve isso: dividir os dados em k partes, treinar e testar k vezes trocando qual parte é o teste, e reportar a média do MAE nas k rodadas. Não está no notebook, mas é o passo natural seguinte.

---

## 5. Exercícios de fixação

**Se o MAE fosse exatamente 0, o que isso significaria?**
Que o modelo acertou a demanda exata em todos os registros de teste — previsão perfeita. Na prática isso quase nunca acontece com dado real; se acontecer, é mais sinal de alerta (vazamento de dado do treino para o teste, ou erro no código) do que de um modelo excelente.

**Por que RMSE é sempre maior ou igual ao MAE?**
Porque o RMSE eleva cada erro ao quadrado antes de tirar a média e depois a raiz — isso penaliza erros grandes desproporcionalmente mais do que erros pequenos. A igualdade só ocorre no caso extremo em que todos os erros têm exatamente o mesmo valor absoluto.

**O que aconteceria com o R² se o modelo simplesmente previsse sempre a média de y, ignorando as features?**
R² seria 0. É por isso que R² serve como régua: 0 é o patamar de um "modelo preguiçoso" que chuta a média sempre; qualquer R² positivo indica que o modelo aprendeu algo além disso.

**Com apenas dois pontos, (x=2, y=4) e (x=6, y=8), qual a reta de mínimos quadrados?**
Com só 2 pontos, a reta passa exatamente pelos dois (erro zero é sempre possível). w1 = (8−4)/(6−2) = 1; w0 = 4 − 1×2 = 2. Reta: ŷ = 2 + x.

**Por que o `train_test_split` embaralha os dados antes de dividir, em vez de pegar os primeiros 80% e os últimos 20%?**
Porque os registros do notebook estão agrupados por produto e ordenados por data. Sem embaralhar, o teste poderia ficar só com as últimas semanas de alguns produtos (ou faltar produtos inteiros no treino) — uma divisão enviesada que não representa bem o problema real.

**O que muda na previsão se `promocao` passa de 0 para 1, mantendo todas as outras features fixas?**
A previsão muda exatamente pelo valor do coeficiente w da feature promocao. Esse é o "efeito isolado" que uma regressão linear atribui a cada feature, e é justamente isso que `modelo.coef_` revela.

---

## 6. Para ir além

Fora do escopo obrigatório da Entrega 03 — mas úteis para responder perguntas mais a fundo, ou para estudo pessoal:

- **Validação cruzada (k-fold)** — estimar a métrica de forma mais robusta do que um único split 80/20.
- **Regularização (Ridge / Lasso)** — o que fazer se, com mais features no futuro, o modelo começar a overfitar: penalizar pesos muito grandes durante o treino.
- **Padronização de features** — comparar os coeficientes de forma justa quando as escalas são muito diferentes (preço em reais vs. promoção 0/1).
- **Continuidade com a Entrega 04** — o mesmo `modelo` treinado aqui será reaproveitado sem retreinar: a previsão de demanda vira a necessidade de reposição que o algoritmo genético tenta atender dentro de um orçamento.
