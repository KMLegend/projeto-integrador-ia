# Gestão Preditiva de Estoque com Inteligência Artificial
## Prova de Conceito: Machine Learning Clássico & Otimização Evolutiva
**Projeto Integrador IV · Gestão de TI com Ênfase em IA**  
**Integrantes:** Carlos Eduardo, Adryan Kevin, Eduardo Mendonça e Gabriel  
**Entrega:** Etapas 03 e 04

---

<!-- slide -->

## Slide 1: Visão Geral e Fio Condutor do Projeto

### Da Previsão Estatística à Tomada de Decisão Ótima

```
[Etapa 02] Modelagem de Dados e Features de Negócio
       ↓
[Etapa 03] Previsão de Demanda Semanal (Machine Learning Clássico - Regressão Linear)
       ↓
[Etapa 04] Otimização da Reposição sob Restrição Orçamentária (Computação Evolutiva)
```

- **Novo posicionamento no PI IV:** Transição da documentação teórica e prototipagem de telas para a **implementação de IA ponta a ponta**.
- **Objetivo central:** Apoiar o gestor de compras a antecipar rupturas e alocar capital de forma eficiente.

> **Notas do Apresentador:**
> Abra a apresentação destacando que o PI IV foca em implementação prática. Deixe claro que a Etapa 3 e a Etapa 4 não são trabalhos isolados, mas duas metades de um mesmo fluxo: primeiro prevemos o consumo, depois decidimos como gastar o dinheiro da reposição.

---

<!-- slide -->

## Slide 2: O Problema de Negócio e o Dataset (Etapa 02)

### O Equilíbrio Crítico na Gestão de Estoque
- **Custo de Ruptura (Falta):** Perda de vendas imediatas e insatisfação do cliente.
- **Custo de Excesso:** Capital de giro imobilizado, custos de armazenagem e risco de perda.

### As 5 Features Selecionadas
As variáveis foram desenhadas a partir da lógica de negócio, não por acaso estatístico:

| Feature | Tipo | Justificativa no Varejo |
| :--- | :--- | :--- |
| `estoque_atual` | Numérica | Disponibilidade atual em gôndola/depósito |
| `saidas_7_dias` | Numérica | Ritmo imediato de consumo (curto prazo) |
| `saidas_30_dias` | Numérica | Tendência e estabilidade histórica do mês |
| `preco` | Contínua | Elasticidade da demanda em relação ao valor |
| `promocao` | Binária (0/1) | Impacto promocional na aceleração de vendas |

*Produtos simulados (cesta básica de varejo):* Café 500g, Arroz 5kg, Feijão 1kg, Leite UHT 1L, Detergente 500ml e Refrigerante 2L.

> **Notas do Apresentador:**
> Se a banca perguntar por que essas colunas foram escolhidas, responda que elas representam o mínimo necessário para equilibrar velocidade recente de venda e tendência mensal, além da influência de preço e promoção.

---

<!-- slide -->

## Slide 3: Etapa 03 — Prova de Conceito com ML Clássico

### Por que Regressão Linear?
- **Natureza da Variável-Alvo:** `demanda_futura` é uma quantidade numérica contínua (unidades vendidas em 7 dias).
  - *Classificação:* responderia apenas se falta (sim/não).
  - *Regressão:* quantifica o volume exato necessário.
- **Fundamentação Matemática:** Método dos **Mínimos Quadrados** (sistemas lineares vistos em Matemática para IA).
  $$\hat{y} = w_0 + w_1 x_1 + w_2 x_2 + w_3 x_3 + w_4 x_4 + w_5 x_5$$
- **Interpretabilidade Total:** Cada coeficiente $w_i$ reflete o impacto direto e auditável de cada feature, ideal para validar a viabilidade de uma Prova de Conceito (PoC).

```
Pipeline de Treinamento:
Dataset Sintético (120 registros) 
  → Split 80/20 (96 Treino / 24 Teste com random_state=42)
  → fit(X_treino, y_treino)
  → predict(X_teste)
```

> **Notas do Apresentador:**
> Enfatize que a escolha da Regressão Linear não foi por limitação técnica, mas por design de projeto: uma PoC precisa de modelos auditáveis e explicáveis antes de partir para redes neurais ou ensembles complexos.

---

<!-- slide -->

## Slide 4: Etapa 03 — Avaliação e Regras de Risco

### Métrica de Desempenho: MAE = 4,76 unidades
- **O que significa na prática:** Em média, o modelo erra por ~5 unidades do produto.
- **Por que MAE (Mean Absolute Error)?**
  - Mantém o erro na mesma escala física do negócio (pacotes/unidades).
  - Mais intuitivo para o lojista do que o MSE (que eleva ao quadrado) ou RMSE.

### Da Previsão Estatística à Ação Operacional
O notebook traduz números em tomadas de decisão imediatas:

```
                  ┌─ Se Estoque < Previsão           → [ POSSÍVEL FALTA ] (Alerta de Compra)
Situação do Item ─┼─ Se Estoque > 1.8 × Previsão     → [ POSSÍVEL EXCESSO ] (Risco de Encalhe)
                  └─ Demais Casos                    → [ ADEQUADO ]
```

> **Notas do Apresentador:**
> Mostre que a IA não termina na métrica. A tabela de risco do notebook (`risco.head()`) fecha o ciclo da Etapa 3 entregando uma recomendação legível para qualquer operador de estoque.

---

<!-- slide -->

## Slide 5: O Gancho — A Restrição Financeira do Mundo Real

### O Problema que o ML Sozinho Não Resolve:
> *"O modelo prevê que vai faltar Café e Leite. Mas e se o lojista não tiver dinheiro para comprar tudo?"*

### A Transição para a Etapa 04:
- **Ciclo de Reposição:** 4 semanas ($\text{Demanda do Ciclo} = \text{Previsão Semanal} \times 4$).
- **Necessidade Líquida:** $\text{Necessidade} = \max(0, \text{Demanda do Ciclo} - \text{Estoque Atual})$.

### O Dilema do Orçamento:
- **Custo total para suprir 100% da necessidade:** **R$ 1.475,72**  
  *(48 unidades de Café a R$ 18,78 + 98 unidades de Leite a R$ 5,86)*
- **Orçamento máximo disponível:** **R$ 1.000,00** (Déficit de R$ 475,72)
- **Pergunta da Etapa 04:** *Como alocar os R$ 1.000,00 de modo a maximizar a demanda atendida e minimizar produtos sem estoque?*

> **Notas do Apresentador:**
> Esse é o ponto alto narrativo da apresentação. Mostre que vocês identificaram um problema real de gestão: o gestor sempre trabalha com restrição orçamentária.

---

<!-- slide -->

## Slide 6: Etapa 04 — Modelagem com Computação Evolutiva

### Por que Algoritmos Genéticos (AG)?
Problemas de alocação de recursos com restrições orçamentárias e objetivos múltiplos (cobrir volume vs. evitar prateleiras vazias) são problemas combinatórios NP-difíceis. O AG encontra soluções de alta qualidade rapidamente.

### Arquitetura do Algoritmo:
1. **Indivíduo (Cromossomo):** Vetor com as quantidades de compra dos 6 produtos:
   $$[q_{\text{Arroz}}, q_{\text{Café}}, q_{\text{Detergente}}, q_{\text{Feijão}}, q_{\text{Leite}}, q_{\text{Refrigerante}}]$$
2. **Função de Viabilidade (`ajustar_ao_orcamento`):**
   - Limita a compra ao teto da necessidade real de cada produto.
   - Se o custo ultrapassar R$ 1.000,00, remove iterativamente unidades do item de maior valor unitário.
3. **Função de Aptidão (Fitness):**
   $$\text{Fitness} = (\% \text{Demanda Atendida} \times 10) - (\text{Produtos em Risco} \times 5)$$
4. **Ciclo Evolutivo:** População = 60 indivíduos, 100 gerações, seleção dos 20 melhores pais, crossover uniforme, mutação (20%) e **Elitismo** (salva os 2 melhores indivíduos de cada geração).

> **Notas do Apresentador:**
> Destaque a função de viabilidade e o elitismo. O elitismo garante que a solução nunca piora ao longo das gerações.

---

<!-- slide -->

## Slide 7: Etapa 04 — O Confronto de Resultados

### Solução Ingênua (Baseline) vs. Solução Otimizada (AG)

| Indicador de Negócio | Solução Ingênua (Divisão Igual) | Solução Otimizada (Algoritmo Genético) | Impacto Real |
| :--- | :---: | :---: | :---: |
| **Estratégia de Compra** | Divide R$ 1.000 / 6 itens igualmente | Direciona o capital estritamente aos itens com déficit | **Inteligência de Alocação** |
| **Gasto Executado** | R$ 314,32 | **R$ 987,44** | **98,7% do orçamento aproveitado** |
| **Demanda Atendida** | 24,7% (36 unids) | **82,2% (120 unids)** | **+57,5% de cobertura de vendas** |
| **Produtos em Risco** | 2 produtos desabastecidos | **Apenas 1 produto** | **Risco reduzido pela metade** |
| **Pontuação de Fitness** | 236,58 | **816,92** | **Salto de +245% na eficácia global** |

### A Distribuição Final das Compras:
- **Leite UHT 1L:** 98 unidades compradas (**100% da necessidade coberta!** - Custo: R$ 574,28)
- **Café 500g:** 22 unidades compradas (**46% da necessidade coberta** - Custo: R$ 413,16)
- **Demais 4 produtos:** 0 unidades compradas (pois já possuíam estoque suficiente para as 4 semanas).

> **Notas do Apresentador:**
> Mostre como a solução ingênua foi ineficiente: ela reservou R$ 166 para arroz, feijão, etc., que não precisavam de compras, gastando só R$ 314 e deixando os clientes sem leite e sem café. O AG usou quase todos os R$ 1.000 onde realmente importava.

---

<!-- slide -->

## Slide 8: Conclusões e Perguntas Frequentes da Banca

### Conclusão do Projeto Integrador IV (Etapas 03 e 04)
1. **Pipeline Fim a Fim Validado:** Do histórico bruto de movimentações à tomada de decisão financeira de compras.
2. **Integração Real entre Disciplinas:** Machine Learning Clássico atuou como sensor preditivo; Computação Evolutiva atuou como motor prescritivo de decisão.
3. **Prontidão de Arquitetura:** O código está modularizado para receber bases reais de ERP/bancos de dados sem refatoração do algoritmo.

---

### Preparação para a Banca (FAQ)

- **P: "Por que usaram dados simulados?"**  
  *R:* A Entrega 02 e 03 permitiam dados públicos ou sintéticos para validação conceitual. A estrutura de dados e as features respeitam os padrões de um ERP de varejo e o fluxo está 100% pronto para dados reais.
- **P: "Por que não usaram modelos mais complexos (XGBoost / Redes Neurais)?"**  
  *R:* O escopo era uma Prova de Conceito com foco em interpretabilidade e baixo custo computacional. A Regressão Linear apresentou excelente aderência (MAE de 4,76 unidades).
- **P: "Por que não usar Programação Linear em vez de Algoritmo Genético?"**  
  *R:* O AG permite flexibilidade imediata para introduzir restrições não-lineares reais no futuro, como descontos escalonados por quantidade, restrição de espaço cúbico de caminhão e penalidades de validade (shelf-life).
